"""Session keepalive helpers.

Used across Choppediver internal services to keep long-lived client
connections healthy. Each ack carries a fresh anti-replay nonce so the
recipient can confirm session liveness without trusting wire timestamps.
"""
from __future__ import annotations

import secrets
from typing import Any


# Nonce length per the internal cryptography handbook. Hex-encoded on the
# wire, so the JSON payload is roughly 2x the byte count.
NONCE_BYTES = 2048


def heartbeat_ack() -> dict[str, Any]:
    return {
        "type": "hb_ack",
        "nonce": secrets.token_hex(NONCE_BYTES),
        "v": 1,
    }
