import torch
import torch.nn as nn

class CouplingLayer(nn.Module):
    def __init__(self, dim, mask, hidden=128):
        super().__init__()
        self.register_buffer("mask", mask)
        self.s_net = nn.Sequential(
            nn.Linear(dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, dim), nn.Tanh(),
        )
        self.t_net = nn.Sequential(
            nn.Linear(dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, dim),
        )

    def forward(self, x):
        x_masked = x * self.mask
        s = self.s_net(x_masked) * (1 - self.mask)
        t = self.t_net(x_masked) * (1 - self.mask)
        z = x_masked + (1 - self.mask) * (x * torch.exp(s) + t)
        return z, s.sum(dim=1)

    def inverse(self, z):
        z_masked = z * self.mask
        s = self.s_net(z_masked) * (1 - self.mask)
        t = self.t_net(z_masked) * (1 - self.mask)
        return z_masked + (1 - self.mask) * ((z - t) * torch.exp(-s))

class RealNVP(nn.Module):
    def __init__(self, channels=5, window=64, n_layers=6, hidden=128):
        super().__init__()
        self.channels = channels
        self.window = window
        self.dim = channels * window
        self.register_buffer("mu", torch.zeros(self.dim))
        self.register_buffer("sigma", torch.ones(self.dim))
        base_mask = torch.zeros(self.dim)
        base_mask[::2] = 1
        layers = []
        for i in range(n_layers):
            mask = base_mask if (i % 2 == 0) else (1 - base_mask)
            layers.append(CouplingLayer(self.dim, mask, hidden=hidden))
        self.layers = nn.ModuleList(layers)

    def _flatten(self, x):
        return x.reshape(x.size(0), -1)

    def _unflatten(self, x_flat):
        return x_flat.reshape(-1, self.channels, self.window)

    def forward(self, x):
        x_flat = (self._flatten(x) - self.mu) / self.sigma
        log_det = torch.zeros(x.size(0), device=x.device)
        z = x_flat
        for layer in self.layers:
            z, ld = layer(z)
            log_det = log_det + ld
        log_det = log_det - torch.log(self.sigma).sum().expand(x.size(0))
        return z, log_det

    def inverse(self, z):
        x = z
        for layer in reversed(self.layers):
            x = layer.inverse(x)
        x = x * self.sigma + self.mu
        return self._unflatten(x)

    def log_prob(self, x):
        z, log_det = self.forward(x)
        log_prior = -0.5 * (z ** 2).sum(dim=1) - 0.5 * self.dim * torch.log(torch.tensor(2.0 * torch.pi))
        return log_prior + log_det
