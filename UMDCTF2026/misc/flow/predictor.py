import torch
import torch.nn as nn
import torch.nn.functional as F

class Predictor(nn.Module):
    def __init__(self, in_ch: int = 5, width: int = 32):
        super().__init__()
        self.c1 = nn.Conv1d(in_ch, width, kernel_size=5, padding=2)
        self.c2 = nn.Conv1d(width, width * 2, kernel_size=5, padding=2)
        self.c3 = nn.Conv1d(width * 2, width * 2, kernel_size=3, padding=1)
        self.head = nn.Linear(width * 2, 2)

    def forward(self, x):
        h = F.relu(self.c1(x))
        h = F.max_pool1d(h, 2)
        h = F.relu(self.c2(h))
        h = F.max_pool1d(h, 2)
        h = F.relu(self.c3(h))
        h = h.mean(dim=2)
        return self.head(h)
