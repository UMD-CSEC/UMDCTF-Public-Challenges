"""Production entrypoint. Applies deploy-specific socket tuning then
launches the server. Not part of the handout."""
from __future__ import annotations

import os
import socket

import server


SO_SNDBUF = int(os.environ.get("SO_SNDBUF", "0"))


def main() -> None:
    if SO_SNDBUF > 0:
        _orig_handler = server.handler

        def tuned_handler(ws):
            ws.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SO_SNDBUF)
            _orig_handler(ws)

        server.handler = tuned_handler

    server.main()


if __name__ == "__main__":
    main()
