# choppediver oa — solve

Run against a deployed WSS endpoint:

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
CHOPP_URL=wss://<host>:<port>/ python3 solve.py
```

Each round saves a PNG to `/tmp/chopp_round_NN.png` and tries to open it
with `xdg-open`. Answer with `b` / `s` / `h` + enter. The script handles
the stall primitive automatically; you just classify.

Needs Linux (uses `TCP_WINDOW_CLAMP`). No root required.
