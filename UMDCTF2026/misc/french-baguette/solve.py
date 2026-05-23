import math
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, milp

EPS = 1e-12

ORDER = "w0_1 w2_3 w4_5 w5_6 b0_1 b2_3 b4_5 b5_6".split()
SIZES = {
    "w0_1": (1, 6, 5, 5),
    "w2_3": (6, 16, 5, 5),
    "w4_5": (16, 120, 5, 5),
    "w5_6": (120, 10),
    "b0_1": (6,),
    "b2_3": (16,),
    "b4_5": (120,),
    "b5_6": (10,),
}

def load_struct(name):
    data = np.fromfile(name, np.float64)
    out = {}
    offset = 0
    for key in ORDER:
        size = math.prod(SIZES[key])
        out[key] = data[offset : offset + size].reshape(SIZES[key]).copy()
        offset += size
    return out

def recover_layer4(grad):
    b45 = int(np.argmax(abs(grad["b4_5"])))
    layer4 = grad["w4_5"][:, b45, :, :] / grad["b4_5"][b45]
    return layer4

def recover_err4(weights, grad, layer4):
    err4 = np.einsum("j,ijkl->ikl", grad["b4_5"], weights["w4_5"])
    err4 = err4 * (layer4 > EPS)
    return err4

def standard_values(n_white):
    p = n_white / 625
    scale = math.sqrt(p * (1 - p))
    black = -p / scale
    white = (1 - p) / scale
    return black, white

def linear_constraint(rows, low, high, n_vars):
    sparse_rows = []
    sparse_cols = []
    sparse_data = []
    for row_idx in range(len(rows)):
        for col_idx in rows[row_idx]:
            value = rows[row_idx][col_idx]
            if value:
                sparse_rows.append(row_idx)
                sparse_cols.append(col_idx)
                sparse_data.append(value)

    matrix = sparse.coo_matrix(
        (sparse_data, (sparse_rows, sparse_cols)),
        shape=(len(rows), n_vars),
    ).tocsr()
    return LinearConstraint(matrix, np.array(low), np.array(high))

def soft_terms(active, err4, layer4):
    layer2_idx = []
    out_idx = []
    choice_idx = []
    coeff = []
    select_b = []
    select_r = []
    select_c = []
    select_v = []
    select_z = []

    for item_idx in range(len(active)):
        b = active[item_idx][0]
        p = active[item_idx][1]
        q = active[item_idx][2]
        for choice in range(4):
            dr = choice // 2
            dc = choice % 2
            select_b.append(b)
            select_r.append(2 * p + dr)
            select_c.append(2 * q + dc)
            select_v.append(layer4[b, p, q])
            select_z.append(4 * item_idx + choice)
            for a in range(6):
                for kh in range(5):
                    for kw in range(5):
                        out_idx.append(((a * 16 + b) * 5 + kh) * 5 + kw)
                        layer2_idx.append((a * 14 + 2 * p + dr + kh) * 14 + 2 * q + dc + kw)
                        choice_idx.append(4 * item_idx + choice)
                        coeff.append(err4[b, p, q])

    return (
        torch.tensor(layer2_idx),
        torch.tensor(out_idx),
        torch.tensor(choice_idx),
        torch.tensor(coeff, dtype=torch.float64),
        torch.tensor(select_b),
        torch.tensor(select_r),
        torch.tensor(select_c),
        torch.tensor(select_v, dtype=torch.float64),
        torch.tensor(select_z),
    )

def soft_pool2_choices(weights, grad, layer4, err4, active, steps=6000):
    torch.manual_seed(0)
    torch.set_num_threads(4)

    dtype = torch.float64
    w23 = torch.tensor(weights["w2_3"].transpose(1, 0, 2, 3), dtype=dtype)
    b23 = torch.tensor(weights["b2_3"], dtype=dtype)
    target = torch.tensor(grad["w2_3"].reshape(-1), dtype=dtype)
    layer4_t = torch.tensor(layer4, dtype=dtype)
    upper = layer4_t.repeat_interleave(2, 1).repeat_interleave(2, 2)
    terms = soft_terms(active, err4, layer4)
    layer2_idx = terms[0]
    out_idx = terms[1]
    choice_idx = terms[2]
    coeff = terms[3]
    select_b = terms[4]
    select_r = terms[5]
    select_c = terms[6]
    select_v = terms[7]
    select_z = terms[8]

    raw = torch.full((6, 14, 14), -0.5, dtype=dtype)
    raw = raw + 0.5 * torch.randn(6, 14, 14, dtype=dtype)
    raw.requires_grad_()
    logits = 0.1 * torch.randn(len(active), 4, dtype=dtype)
    logits.requires_grad_()
    opt = torch.optim.Adam([raw, logits], lr=0.03)

    for step in range(steps):
        temp = max(0.06, 2.0 * (0.06 / 2.0) ** (step / (steps - 1000)))
        layer2 = F.softplus(raw, beta=4).reshape(-1)
        choices = F.softmax(logits / temp, 1).reshape(-1)

        pred = torch.zeros(2400, dtype=dtype)
        pred.index_add_(
            0,
            out_idx,
            coeff * choices[choice_idx] * layer2[layer2_idx],
        )
        pre = F.conv2d(layer2.reshape(1, 6, 14, 14), w23, b23)[0]
        loss = 1e5 * ((pred - target) ** 2).sum()
        loss = loss + 20 * (F.relu(pre - upper) ** 2).sum()
        selected = pre[select_b, select_r, select_c]
        loss = loss + 20 * (choices[select_z] * (selected - select_v) ** 2).sum()

        opt.zero_grad()
        loss.backward()
        opt.step()

        if step % 1000 == 0 or step == steps - 1:
            print(f"soft step {step}: loss={loss.item():.3e}")

    return logits.argmax(1).detach().numpy().astype(np.int8)

def pool2_matrix_data(active, err4):
    rows = np.zeros((len(active), 4, 25), np.int32)
    cols = np.zeros_like(rows)
    vals = np.zeros((len(active), 4, 25))
    for item_idx in range(len(active)):
        b = active[item_idx][0]
        p = active[item_idx][1]
        q = active[item_idx][2]
        for choice in range(4):
            dr = choice // 2
            dc = choice % 2
            for kh in range(5):
                for kw in range(5):
                    idx = 5 * kh + kw
                    rows[item_idx, choice, idx] = 25 * b + 5 * kh + kw
                    cols[item_idx, choice, idx] = 14 * (2 * p + dr + kh) + 2 * q + dc + kw
                    vals[item_idx, choice, idx] = err4[b, p, q]
    return rows, cols, vals

def add_choice(matrix, rows, cols, vals, item_idx, choice, sign):
    matrix[rows[item_idx, choice], cols[item_idx, choice]] += sign * vals[item_idx, choice]

def solve_l2(matrix, grad):
    rhs = np.stack([grad["w2_3"][i].reshape(-1) for i in range(6)], 1)
    sol = np.linalg.lstsq(matrix, rhs, rcond=None)[0]
    residual = matrix @ sol - rhs
    score = float((residual * residual).sum())
    layer2 = sol.T.reshape(6, 14, 14)
    return score, layer2

def recover_layer2(weights, grad, layer4, err4):
    active = np.argwhere(abs(err4) > EPS)
    choices = soft_pool2_choices(weights, grad, layer4, err4, active)
    pool2_data = pool2_matrix_data(active, err4)
    rows = pool2_data[0]
    cols = pool2_data[1]
    vals = pool2_data[2]
    matrix = np.zeros((400, 196))

    for item_idx in range(len(choices)):
        add_choice(matrix, rows, cols, vals, item_idx, int(choices[item_idx]), 1)

    residual_result = solve_l2(matrix, grad)
    residual = residual_result[0]
    layer2 = residual_result[1]
    rng = np.random.default_rng(0)

    for sweep in range(8):
        changed = 0
        for item_idx in rng.permutation(len(choices)):
            old_choice = int(choices[item_idx])
            best_choice = old_choice
            best_residual = residual
            best_layer2 = layer2

            for choice in range(4):
                if choice == old_choice:
                    continue
                add_choice(matrix, rows, cols, vals, item_idx, old_choice, -1)
                add_choice(matrix, rows, cols, vals, item_idx, choice, 1)
                candidate = solve_l2(matrix, grad)
                add_choice(matrix, rows, cols, vals, item_idx, choice, -1)
                add_choice(matrix, rows, cols, vals, item_idx, old_choice, 1)

                if candidate[0] < best_residual - 1e-16:
                    best_residual = candidate[0]
                    best_choice = choice
                    best_layer2 = candidate[1]

            if best_choice != old_choice:
                add_choice(matrix, rows, cols, vals, item_idx, old_choice, -1)
                add_choice(matrix, rows, cols, vals, item_idx, best_choice, 1)
                choices[item_idx] = best_choice
                residual = best_residual
                layer2 = best_layer2
                changed += 1

        print(f"pool2 sweep {sweep}: residual={residual:.3e}, changed={changed}")
        if residual < 1e-24 or changed == 0:
            break

    assert residual < 1e-24
    return layer2

def conv1_terms(weights):
    out = {}
    for c in range(6):
        for r in range(28):
            for s in range(28):
                bias = weights["b0_1"][c]
                total = 0.0
                coeffs = {}
                for kh in range(5):
                    for kw in range(5):
                        rr = r + kh - 2
                        cc = s + kw - 2
                        if 0 <= rr < 25 and 0 <= cc < 25:
                            idx = 25 * rr + cc
                            weight = weights["w0_1"][0, c, kh, kw]
                            total += weight
                            coeffs[idx] = coeffs.get(idx, 0.0) + weight
                out[c, r, s] = (float(bias), float(total), coeffs)
    return out

def first_layer_milp(layer2, n_white, terms):
    values = standard_values(n_white)
    black = values[0]
    white = values[1]
    delta = white - black
    positive = [
        (c, r, s)
        for c in range(6)
        for r in range(14)
        for s in range(14)
        if layer2[c, r, s] > EPS
    ]
    positive_idx = {value: idx for idx, value in enumerate(positive)}

    n_vars = 625 + 4 * len(positive)
    rows = []
    low = []
    high = []

    def add(row, lower, upper):
        rows.append(row)
        low.append(lower)
        high.append(upper)

    add({idx: 1.0 for idx in range(625)}, n_white, n_white)

    for c in range(6):
        for r in range(14):
            for s in range(14):
                value = 0.0
                if layer2[c, r, s] > EPS:
                    value = float(layer2[c, r, s])
                    pos = positive_idx[c, r, s]
                    choice_row = {}
                    for choice in range(4):
                        choice_row[625 + 4 * pos + choice] = 1.0
                    add(choice_row, 1, 1)

                for choice in range(4):
                    term = terms[c, 2 * r + choice // 2, 2 * s + choice % 2]
                    const = term[0] + term[1] * black
                    coeffs = {idx: value * delta for idx, value in term[2].items()}
                    add(coeffs.copy(), -np.inf, value - const)

                    if value > 0.0:
                        lower_bound = const
                        for coeff in coeffs.values():
                            if coeff < 0.0:
                                lower_bound += coeff
                        big_m = value - lower_bound + 1e-8
                        row = coeffs.copy()
                        row[625 + 4 * pos + choice] = row.get(625 + 4 * pos + choice, 0.0) - big_m
                        add(row, value - big_m - const, np.inf)

    return milp(
        np.zeros(n_vars),
        integrality=np.ones(n_vars),
        bounds=Bounds(np.zeros(n_vars), np.ones(n_vars)),
        constraints=linear_constraint(rows, low, high, n_vars),
        options={"time_limit": 1.0, "mip_rel_gap": 0},
    )

def render_and_save(qr):
    raw = np.where(qr, 255, 0).astype(np.uint8)
    padded = np.pad(raw, 4, constant_values=255)
    image = np.repeat(np.repeat(padded, 20, 0), 20, 1)
    Image.fromarray(image).save("solve_qr.png")

def main():
    weights = load_struct("model.dat")
    grad = load_struct("grad.dat")
    layer4 = recover_layer4(grad)
    err4 = recover_err4(weights, grad, layer4)
    layer2 = recover_layer2(weights, grad, layer4, err4)
    terms = conv1_terms(weights)
    solutions = []

    for n_white in range(1, 625):
        result = first_layer_milp(layer2, n_white, terms)
        if result.success and result.x is not None:
            qr = np.rint(result.x[:625]).astype(np.uint8).reshape(25, 25)
            solutions.append((n_white, qr))
            print(f"feasible white_count={n_white}")

    assert len(solutions) == 1
    n_white = solutions[0][0]
    qr = solutions[0][1]
    render_and_save(qr)

if __name__ == "__main__":
    main()
