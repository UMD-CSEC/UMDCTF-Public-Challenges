from z3 import *

# UMDCTF{n3uR4Ln37w0rk5}
real_input = [
    85,
    77,
    68,
    67,
    84,
    70,
    123,
    110,
    51,
    117,
    82,
    52,
    76,
    110,
    51,
    55,
    119,
    48,
    114,
    107,
    53,
    125,
]

layers = [[[], []]]
data = open("./model.txt", "r").readlines()
biases = False
for l in data:
    l = l.strip()
    if "layer" in l:
        i = int(l[-1])
        layers.append([[], []])
    elif "biases" in l:
        biases = True
    elif "weights" in l:
        biases = False
    elif len(l) > 0:
        nums = [RealVal(x) for x in l.split(" ")]
        if biases:
            layers[i][1] += nums
        else:
            layers[i][0] += nums

layer_data = []
layer_data.append([RealVal(x) for x in real_input])
for i in range(1, len(layers)):
    layer_data.append([])
    for j in range(len(layers[i][1])):
        n = RealVal(0)
        for k in range(len(layer_data[i - 1])):
            n += layer_data[i - 1][k] * layers[i][0][j * len(layer_data[i - 1]) + k]
        n += layers[i][1][j]
        layer_data[-1].append(n)

s = Solver()
vars = []
for i in range(len(layer_data[-1])):
    vars.append(Real(str(i)))
    s.add(vars[i] == layer_data[-1][i])

s.check()
print(s.model())
outputs = " ".join(
    [
        y[1]
        for y in sorted(
            [
                x.split("=")
                for x in str(s.model())[1:-1]
                .replace("\n", "")
                .replace(" ", "")
                .split(",")
            ],
            key=lambda x: int(x[0]),
        )
    ]
)
with open("outputs.txt", "w") as f:
    f.write(outputs)
