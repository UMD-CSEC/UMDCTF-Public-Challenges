"""
Per-connection supervisor for the BREACH challenge.

Listens on a TCP port. For each incoming connection:
  1. Picks a unique session id (SID).
  2. Builds a private LAN: three netns (admin/server/player) bridged together.
  3. Launches the server + admin Python processes in their respective netns.
  4. Execs nsjail with bash inside the player netns, wiring the TCP socket to bash's stdio.
  5. On disconnect or timeout, kills the processes and tears down the namespaces.

Requires: root (or CAP_NET_ADMIN + CAP_SYS_ADMIN), iproute2, nsjail, python3,
and the challenge's src/ and certs/ directories at known paths.

Runs as the container's entrypoint.
"""
import contextlib
import os
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "31337"))
SESSION_TIMEOUT = int(os.environ.get("SESSION_TIMEOUT", "3600"))  # 1 hour default
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "2048"))

# The flag is baked in at image build time.
FLAG = os.environ["FLAG"]

# The admin credentials are generated fresh on supervisor startup — they never
# appear in any config file, image layer, or handout. The supervisor shares
# them with the server and admin processes via env, and nothing else sees them.
ADMIN_USER = "admin"
ADMIN_PASS = secrets.token_urlsafe(24)

# Paths inside the container image.
CHALL_DIR = os.environ.get("CHALL_DIR", "/opt/breach")
SRC_DIR = f"{CHALL_DIR}/src"
CERTS_DIR = f"{CHALL_DIR}/certs"
PLAYER_ROOT = os.environ.get("PLAYER_ROOT", "/opt/breach/player-root")
NSJAIL = os.environ.get("NSJAIL", "/usr/local/bin/nsjail")

# All sessions share the same /24 (10.0.0.0/24) inside their own netns tree.
# This is safe because each session lives in an isolated set of network
# namespaces — the host kernel tracks them independently by namespace id,
# so identical addresses across sessions don't collide.
# IP assignment within the subnet:
#   .1 = admin, .2 = server, .3 = player
ADMIN_IP = "10.0.0.1"
SERVER_IP = "10.0.0.2"
PLAYER_IP = "10.0.0.3"
SUBNET_MASK = "24"

concurrency_sem = threading.BoundedSemaphore(MAX_CONCURRENT)


def log(msg: str) -> None:
    print(f"[supervisor] {msg}", file=sys.stderr, flush=True)


def run(cmd: list[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Run a shell command; raise on nonzero exit if check=True."""
    return subprocess.run(cmd, check=check, **kwargs)


class Session:
    def __init__(self, sid: str, client_sock: socket.socket) -> None:
        self.sid = sid
        self.client = client_sock
        self.procs: list[subprocess.Popen] = []
        self.netns = {
            "admin": f"ba-{sid}",
            "server": f"bs-{sid}",
            "player": f"bp-{sid}",
        }
        self.bridge = f"bb-{sid}"
        # veth names: outer half (bridge side) + inner half (netns side)
        self.veth = {
            "admin":  (f"va-o-{sid}", f"va-i-{sid}"),
            "server": (f"vs-o-{sid}", f"vs-i-{sid}"),
            "player": (f"vp-o-{sid}", f"vp-i-{sid}"),
        }

    # --- network construction ---

    def build_net(self) -> None:
        # Bridge in outer netns
        run(["ip", "link", "add", self.bridge, "type", "bridge"])
        run(["ip", "link", "set", self.bridge, "up"])

        # Create netns
        for role in ("admin", "server", "player"):
            run(["ip", "netns", "add", self.netns[role]])

        # Create veths, attach outer half to bridge, inner half to netns, assign IPs
        ips = {
            "admin": ADMIN_IP,
            "server": SERVER_IP,
            "player": PLAYER_IP,
        }
        for role in ("admin", "server", "player"):
            outer, inner = self.veth[role]
            ns = self.netns[role]
            ip = ips[role]
            run(["ip", "link", "add", outer, "type", "veth", "peer", "name", inner])
            run(["ip", "link", "set", outer, "master", self.bridge])
            run(["ip", "link", "set", outer, "up"])
            run(["ip", "link", "set", inner, "netns", ns])
            run(["ip", "-n", ns, "addr", "add", f"{ip}/{SUBNET_MASK}", "dev", inner])
            run(["ip", "-n", ns, "link", "set", inner, "up"])
            run(["ip", "-n", ns, "link", "set", "lo", "up"])

        # No default gateway — the LAN is island, no outbound.

    def tear_net(self) -> None:
        for ns in self.netns.values():
            run(["ip", "netns", "delete", ns], check=False,
                stderr=subprocess.DEVNULL)
        run(["ip", "link", "delete", self.bridge], check=False,
            stderr=subprocess.DEVNULL)

    # --- launching processes ---

    def launch_server(self) -> None:
        env = {
            **os.environ,
            "FLAG": FLAG,
            "ADMIN_USER": ADMIN_USER,
            "ADMIN_PASS": ADMIN_PASS,
            "BIND_HOST": SERVER_IP,
            "BIND_PORT": "443",
            "CERT_FILE": f"{CERTS_DIR}/cert.pem",
            "KEY_FILE": f"{CERTS_DIR}/key.pem",
        }
        p = subprocess.Popen(
            ["ip", "netns", "exec", self.netns["server"],
             "python3", f"{SRC_DIR}/server.py"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.procs.append(p)

    def launch_admin(self) -> None:
        env = {
            **os.environ,
            "SERVER_HOST": SERVER_IP,
            "SERVER_PORT": "443",
            "ADMIN_USER": ADMIN_USER,
            "ADMIN_PASS": ADMIN_PASS,
            "INTERVAL": "0.05",
        }
        p = subprocess.Popen(
            ["ip", "netns", "exec", self.netns["admin"],
             "python3", f"{SRC_DIR}/admin.py"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.procs.append(p)

    def _watchdog_kick(self, proc: subprocess.Popen) -> None:
        """Belt-and-suspenders: SIGKILL the player shell after SESSION_TIMEOUT.

        proc.wait(timeout=...) is the primary kick, but if a signal interrupts
        wait() or the socket fd plays games with read(), the watchdog still
        guarantees the session ends on schedule.
        """
        time.sleep(SESSION_TIMEOUT)
        with contextlib.suppress(ProcessLookupError, OSError):
            if proc.poll() is None:
                proc.kill()
        with contextlib.suppress(Exception):
            self.client.shutdown(socket.SHUT_RDWR)

    def _disconnect_watcher(self, proc: subprocess.Popen) -> None:
        """Detect TCP disconnect (peer closed) and kill the player shell.
        Without this, a player nc-disconnect doesn't end the session — bash
        holds fds open through children and the supervisor waits the full
        SESSION_TIMEOUT, blocking the IP from reconnecting.

        Uses POLLRDHUP which fires when the peer closes its half of the
        connection, regardless of whether bytes are still buffered.
        """
        import select
        try:
            sock_dup = self.client.dup()
        except OSError:
            return
        try:
            poller = select.poll()
            # POLLRDHUP: peer closed sending side. POLLHUP: full hangup.
            # POLLERR: socket error.
            poller.register(
                sock_dup.fileno(),
                select.POLLRDHUP | select.POLLHUP | select.POLLERR,
            )
            while proc.poll() is None:
                events = poller.poll(1000)  # 1s timeout, then re-check proc
                if events:
                    # Any of the registered events means the peer is gone.
                    break
        finally:
            with contextlib.suppress(Exception):
                sock_dup.close()
            with contextlib.suppress(ProcessLookupError, OSError):
                if proc.poll() is None:
                    proc.kill()

    def run_player_shell(self) -> None:
        """Block until the player disconnects or the session times out."""
        # nsjail args:
        #   --mode o : run once, one session
        #   --chroot  : player's rootfs
        #   --user/--group : uid/gid inside jail
        #   --disable_clone_newnet : use the pre-existing player netns
        #   --cap CAP_NET_RAW, CAP_NET_ADMIN : for arpspoof + tcpdump + ip tooling
        #   --rlimit_as/cpu/etc: resource caps
        #   --time_limit : hard timeout
        #   -- /bin/bash : what to exec
        argv = [
            "ip", "netns", "exec", self.netns["player"],
            NSJAIL,
            "--mode", "o",
            "--chroot", PLAYER_ROOT,
            "--user", "1000",
            "--group", "1000",
            "--disable_clone_newnet",
            "--disable_clone_newuser",     # keep caps visible inside the sandbox
            "--keep_caps",
            "--cap", "CAP_NET_RAW",
            "--cap", "CAP_NET_ADMIN",
            "--rlimit_as", "512",
            "--rlimit_cpu", str(SESSION_TIMEOUT + 60),
            "--rlimit_nproc", "64",
            "--time_limit", str(SESSION_TIMEOUT),
            "--proc_rw",                   # writable /proc for ip/ss tools
            "--tmpfsmount", "/tmp",        # writable /tmp
            "--tmpfsmount", "/home/player", # writable home for player scripts
            "--env", "HOME=/home/player",
            "--env", "TERM=xterm",
            "--env", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "--bindmount", "/dev/null",
            "--bindmount", "/dev/zero",
            "--bindmount", "/dev/urandom",
            "--bindmount", "/dev/tty",
            "--quiet",
            "--",
            "/bin/bash", "-i",
        ]
        # Wire the TCP socket to nsjail's stdin/stdout/stderr.
        fd = self.client.fileno()
        proc = subprocess.Popen(
            argv,
            stdin=fd,
            stdout=fd,
            stderr=fd,
            close_fds=False,
        )
        self.procs.append(proc)
        watchdog = threading.Thread(
            target=self._watchdog_kick, args=(proc,), daemon=True
        )
        watchdog.start()
        disconnect_watcher = threading.Thread(
            target=self._disconnect_watcher, args=(proc,), daemon=True
        )
        disconnect_watcher.start()
        try:
            proc.wait(timeout=SESSION_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    # --- top-level lifecycle ---

    def kill_all(self) -> None:
        for p in self.procs:
            with contextlib.suppress(ProcessLookupError, OSError):
                p.terminate()
        time.sleep(0.5)
        for p in self.procs:
            with contextlib.suppress(ProcessLookupError, OSError):
                p.kill()

    def run(self) -> None:
        log(f"[{self.sid}] session start")
        try:
            self.build_net()
            self.launch_server()
            time.sleep(0.5)  # give server a moment to bind
            self.launch_admin()
            self.run_player_shell()
        except Exception as e:
            log(f"[{self.sid}] error: {e!r}")
        finally:
            self.kill_all()
            self.tear_net()
            with contextlib.suppress(Exception):
                self.client.close()
            log(f"[{self.sid}] session end")


def handle_connection(client: socket.socket) -> None:
    acquired = concurrency_sem.acquire(blocking=False)
    if not acquired:
        log(f"reject: server full ({MAX_CONCURRENT} concurrent)")
        with contextlib.suppress(Exception):
            client.sendall(b"server busy, try again shortly\n")
            client.close()
        return
    try:
        sid = secrets.token_hex(4)
        Session(sid, client).run()
    finally:
        concurrency_sem.release()


def main() -> None:
    # Sanity checks
    for path in (SRC_DIR, CERTS_DIR, PLAYER_ROOT, NSJAIL):
        if not os.path.exists(path):
            log(f"FATAL: missing path {path}")
            sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    sock.listen(512)
    log(f"listening on {LISTEN_HOST}:{LISTEN_PORT}")

    # Clean shutdown on SIGTERM
    def shutdown(signum, frame):
        log(f"received signal {signum}, shutting down")
        sock.close()
        sys.exit(0)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        client, addr = sock.accept()
        log(f"accept from {addr}")
        t = threading.Thread(target=handle_connection, args=(client,), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
