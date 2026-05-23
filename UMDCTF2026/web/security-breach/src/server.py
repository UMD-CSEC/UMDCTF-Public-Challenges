import gzip
import json
import os
import re
import secrets
import ssl
import sys
import threading
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    import brotli  # type: ignore
    _HAS_BROTLI = True
except ImportError:
    _HAS_BROTLI = False

def _required(name: str) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        print(f"[server] FATAL: required env var {name} is unset", file=sys.stderr)
        sys.exit(1)
    return v


ADMIN_USER = _required("ADMIN_USER")
ADMIN_PASS = _required("ADMIN_PASS")
FLAG = _required("FLAG")
ADMIN_SESSION = secrets.token_hex(16)

BIND_HOST = os.environ.get("BIND_HOST", "127.0.0.1")
BIND_PORT = int(os.environ.get("BIND_PORT", "4443"))
CERT_FILE = os.environ.get("CERT_FILE", "certs/cert.pem")
KEY_FILE = os.environ.get("KEY_FILE", "certs/key.pem")

MAX_FILTER_LEN = 128
FILTER_RE = re.compile(r"^[A-Za-z0-9_{}]*$")

DASHBOARD_TEMPLATE = '{{"filter":"{filter}","flag":"{flag}"}}'

state_lock = threading.Lock()
latest_suggestion = ""


def _compress_gzip(data: bytes) -> bytes:
    return gzip.compress(data, compresslevel=6, mtime=0)


def _compress_deflate(data: bytes) -> bytes:
    return zlib.compress(data, 6)


def _compress_br(data: bytes) -> bytes:
    if not _HAS_BROTLI:
        raise RuntimeError("brotli not available")
    return brotli.compress(data, quality=6)


_ENCODERS = [
    ("gzip", _compress_gzip),
    ("br", _compress_br if _HAS_BROTLI else None),
    ("deflate", _compress_deflate),
]


def pick_encoding(accept_encoding: str):
    """Return (name, encoder) for the first server-preferred codec the client
    lists in its Accept-Encoding. Falls back to (None, None) for identity."""
    accepted = {
        p.strip().split(";", 1)[0].lower()
        for p in (accept_encoding or "").split(",")
    }
    for name, fn in _ENCODERS:
        if fn is not None and name in accepted:
            return name, fn
    return None, None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[server] " + (fmt % args) + "\n")

    def _session_ok(self) -> bool:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "session" and v == ADMIN_SESSION:
                return True
        return False

    def _send(self, status, body, *, encoding=None,
              content_type="application/json", extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if encoding:
            self.send_header("Content-Encoding", encoding)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "keep-alive")
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, separators=(",", ":")).encode())

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/api/dashboard":
            if not self._session_ok():
                self._json(401, {"error": "login required"})
                return
            with state_lock:
                q = latest_suggestion
            body = DASHBOARD_TEMPLATE.format(filter=q, flag=FLAG).encode()
            enc_name, enc_fn = pick_encoding(self.headers.get("Accept-Encoding", ""))
            if enc_fn is not None:
                body = enc_fn(body)
            self._send(200, body, encoding=enc_name)
            return

        if url.path == "/api/suggestions/latest":
            with state_lock:
                q = latest_suggestion
            self._json(200, {"filter": q})
            return

        if url.path == "/":
            self._json(200, {
                "service": "umdmarket insider dashboard",
                "endpoints": [
                    "POST /login",
                    "POST /api/suggestions",
                    "GET  /api/suggestions/latest",
                    "GET  /api/dashboard?filter=<q>  (admin-only)",
                ],
            })
            return

        self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        global latest_suggestion
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""

        if url.path == "/login":
            form = parse_qs(raw.decode(errors="replace"))
            if (form.get("user", [""])[0] == ADMIN_USER
                    and form.get("pass", [""])[0] == ADMIN_PASS):
                self._send(
                    200, b'{"ok":true}',
                    extra_headers={"Set-Cookie": f"session={ADMIN_SESSION}; Path=/"},
                )
            else:
                self._json(401, {"error": "bad credentials"})
            return

        if url.path == "/api/suggestions":
            q = ""
            ct = self.headers.get("Content-Type", "")
            if ct.startswith("application/json"):
                try:
                    q = (json.loads(raw or b"{}").get("filter") or "")
                except Exception:
                    q = ""
            else:
                q = parse_qs(raw.decode(errors="replace")).get("filter", [""])[0]
            if len(q) > MAX_FILTER_LEN or not FILTER_RE.match(q):
                self._json(400, {"error": "bad filter"})
                return
            with state_lock:
                latest_suggestion = q
            self._json(200, {"ok": True})
            return

        self._send(404, b'{"error":"not found"}')


def build_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    return ctx


def main():
    srv = ThreadingHTTPServer((BIND_HOST, BIND_PORT), Handler)
    srv.socket = build_ssl_context().wrap_socket(srv.socket, server_side=True)
    print(f"[server] https://{BIND_HOST}:{BIND_PORT}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
