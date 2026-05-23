import numpy as np

WINDOW = 64
N_CHANNELS = 5

def simulate_path(n_bars, rng):
    omega, alpha, beta = 1e-6, 0.08, 0.90
    sigma2 = np.zeros(n_bars)
    sigma2[0] = omega / (1 - alpha - beta)
    r = np.zeros(n_bars)
    r[0] = rng.normal(0, np.sqrt(sigma2[0]))
    mom_k, mom_strength = 8, 0.55
    for t in range(1, n_bars):
        sigma2[t] = omega + alpha * r[t - 1] ** 2 + beta * sigma2[t - 1]
        mom = r[max(0, t - mom_k):t].mean() if t >= 2 else 0.0
        r[t] = mom_strength * mom + rng.normal(0, np.sqrt(sigma2[t]))

    close = 100.0 * np.exp(np.cumsum(0.0002 + r))
    intra = np.abs(rng.normal(0, np.sqrt(sigma2) * 0.5, size=n_bars))
    high = close * (1 + intra)
    low = close * (1 - intra)
    gap = rng.normal(0, np.sqrt(sigma2) * 0.3, size=n_bars)
    open_ = np.concatenate([[close[0]], close[:-1]]) * np.exp(gap)
    high = np.maximum.reduce([high, open_, close])
    low = np.minimum.reduce([low, open_, close])
    volume = 1e6 * np.exp(2.0 * np.abs(r) / np.sqrt(sigma2 + 1e-12) + rng.normal(0, 0.3, size=n_bars))
    return np.stack([open_, high, low, close, volume], axis=1).astype(np.float32)

def ohlcv_to_features(raw):
    prev_close = np.concatenate([[raw[0, 3]], raw[:-1, 3]])
    log_o = np.log(raw[:, 0] / prev_close)
    log_h = np.log(raw[:, 1] / prev_close)
    log_l = np.log(raw[:, 2] / prev_close)
    log_c = np.log(raw[:, 3] / prev_close)
    lv = np.log(raw[:, 4] + 1e-9)
    lv = (lv - lv.mean()) / (lv.std() + 1e-9)
    return np.stack([log_o, log_h, log_l, log_c, lv], axis=0).astype(np.float32)

def label_from_features(feats, rng):
    close_r = feats[3]; vol = feats[4]
    high_r = feats[1]; low_r = feats[2]
    mom = close_r[-16:].sum()
    mom_short = close_r[-8:].sum() - close_r[-16:-8].sum()
    rng_recent = (high_r[-16:] - low_r[-16:]).mean()
    vol_trend = vol[-8:].mean() - vol[-24:-8].mean()
    signal = 120.0 * mom + 90.0 * mom_short - 40.0 * rng_recent + 0.4 * vol_trend
    return int(rng.random() < 1.0 / (1.0 + np.exp(-signal)))

def make_dataset(n_samples, seed=0):
    rng = np.random.default_rng(seed)
    X = np.empty((n_samples, N_CHANNELS, WINDOW), dtype=np.float32)
    y = np.empty((n_samples,), dtype=np.int64)
    for i in range(n_samples):
        feats = ohlcv_to_features(simulate_path(WINDOW, rng))
        X[i] = feats
        y[i] = label_from_features(feats, rng)
    return X, y
