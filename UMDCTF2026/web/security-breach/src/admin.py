import http.client
import os
import ssl
import sys
import time
import urllib.parse

def _required(name: str) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        print(f"[admin] FATAL: required env var {name} is unset", file=sys.stderr)
        sys.exit(1)
    return v


SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "4443"))
ADMIN_USER = _required("ADMIN_USER")
ADMIN_PASS = _required("ADMIN_PASS")
INTERVAL = float(os.environ.get("INTERVAL", "0.05"))


def build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def login(conn: http.client.HTTPSConnection) -> str:
    body = urllib.parse.urlencode({"user": ADMIN_USER, "pass": ADMIN_PASS})
    conn.request(
        "POST", "/login", body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
            "Connection": "keep-alive",
        },
    )
    resp = conn.getresponse()
    cookie = resp.getheader("Set-Cookie", "")
    resp.read()
    if not cookie:
        raise RuntimeError("admin login failed")
    return cookie.split(";", 1)[0]


def fetch_dashboard(conn: http.client.HTTPSConnection, cookie: str) -> None:
    conn.request(
        "GET", "/api/dashboard",
        headers={
            "Cookie": cookie,
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
        },
    )
    resp = conn.getresponse()
    resp.read()


def main():
    ctx = build_ssl_context()
    while True:
        try:
            conn = http.client.HTTPSConnection(SERVER_HOST, SERVER_PORT, context=ctx)
            conn.connect()
            cookie = login(conn)
            print(f"[admin] logged in, cookie={cookie}", file=sys.stderr, flush=True)
            while True:
                fetch_dashboard(conn, cookie)
                time.sleep(INTERVAL)
        except Exception as e:
            print(f"[admin] error: {e!r}; reconnecting", file=sys.stderr, flush=True)
            time.sleep(1)


if __name__ == "__main__":
    main()
