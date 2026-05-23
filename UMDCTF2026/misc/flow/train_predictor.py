from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from data import make_dataset
from predictor import Predictor

HERE = Path(__file__).parent

def main(n_train=20000, n_val=2000, epochs=8):
    torch.manual_seed(0)
    Xtr, ytr = make_dataset(n_train, seed=1)
    Xva, yva = make_dataset(n_val, seed=2)

    train_dl = DataLoader(TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr)), batch_size=256, shuffle=True)
    val_dl = DataLoader(TensorDataset(torch.from_numpy(Xva), torch.from_numpy(yva)), batch_size=512)

    model = Predictor()
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)
    for ep in range(epochs):
        model.train()
        tot = n = 0
        for xb, yb in train_dl:
            loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * xb.size(0); n += xb.size(0)
        model.eval()
        with torch.no_grad():
            correct = total = 0
            for xb, yb in val_dl:
                correct += (model(xb).argmax(1) == yb).sum().item(); total += xb.size(0)
        print(f"ep {ep+1}/{epochs}  loss={tot/n:.4f}  val_acc={correct/total:.3f}")

    out = HERE / "dist" / "predictor.pt"
    torch.save(model.state_dict(), out)
    print("saved", out)

if __name__ == "__main__":
    main()
