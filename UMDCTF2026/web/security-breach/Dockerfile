# syntax=docker/dockerfile:1
# ---------- nsjail binary ----------
FROM pwn.red/jail AS jail-src

# ---------- final image ----------
FROM debian:stable-slim

# Tools the *outer supervisor* needs (iproute2, openssl for cert gen, python3)
# plus tools the *player* needs inside their sandboxed bash
# (bash, curl, python3, tcpdump, dsniff for arpspoof, jq, nc, iproute2).
# dsniff is what gives us /usr/sbin/arpspoof.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      bash binutils ca-certificates coreutils curl dsniff gzip iproute2 \
      iputils-ping jq libnl-3-200 libnl-route-3-200 libprotobuf32t64 \
      ncat netcat-openbsd nmap openssl procps python3 python3-brotli \
      python3-pip python3-requests socat tcpdump vim-tiny xxd \
 && rm -rf /var/lib/apt/lists/*

# nsjail binary
COPY --from=jail-src /jail/nsjail /usr/local/bin/nsjail
RUN chmod +x /usr/local/bin/nsjail

# Challenge files
WORKDIR /opt/breach
COPY src/ /opt/breach/src/
COPY infra/ /opt/breach/infra/
COPY certs/ /opt/breach/certs/

# --- player rootfs ---
# nsjail chroots the player into /opt/breach/player-root. We build a minimal
# rootfs there by copying just what the player's shell needs.
RUN mkdir -p /opt/breach/player-root \
 && cd /opt/breach/player-root \
 && mkdir -p bin sbin lib lib64 usr/bin usr/sbin usr/lib usr/lib64 \
             etc tmp home/player dev proc var/lib/dpkg \
 && cp -a /bin/. bin/ \
 && cp -a /sbin/. sbin/ \
 && cp -a /usr/bin/. usr/bin/ \
 && cp -a /usr/sbin/. usr/sbin/ \
 && cp -a /lib/. lib/ \
 && cp -a /lib64/. lib64/ 2>/dev/null || true \
 && cp -a /usr/lib/. usr/lib/ \
 && cp -a /usr/lib64/. usr/lib64/ 2>/dev/null || true \
 && cp -a /etc/alternatives etc/alternatives \
 && cp -a /etc/ssl etc/ssl \
 && cp /etc/nsswitch.conf etc/nsswitch.conf 2>/dev/null || true \
 && cp /etc/resolv.conf etc/resolv.conf 2>/dev/null || echo "" > etc/resolv.conf \
 && echo 'root:x:0:0:root:/root:/bin/bash' > etc/passwd \
 && echo 'player:x:1000:1000:player:/home/player:/bin/bash' >> etc/passwd \
 && echo 'root:x:0:' > etc/group \
 && echo 'player:x:1000:' >> etc/group \
 && chmod 755 home/player

COPY infra/notes.md /opt/breach/player-root/etc/notes.md
# bashrc: nsjail mounts a fresh tmpfs on /home/player each session, so we
# seed notes.md from /etc on first interactive shell load.
RUN printf '%s\n' \
      'export PS1="player@insider-market:\w\$ "' \
      'cd /home/player' \
      '[[ ! -f /home/player/notes.md ]] && cp /etc/notes.md /home/player/notes.md 2>/dev/null' \
      > /opt/breach/player-root/etc/bash.bashrc

# Generate self-signed cert at build time (regenerated per container build)
RUN mkdir -p /opt/breach/certs \
 && openssl req -x509 -newkey rsa:2048 \
      -keyout /opt/breach/certs/key.pem -out /opt/breach/certs/cert.pem \
      -sha256 -days 3650 -nodes -subj "/CN=insider-market" \
      -addext "subjectAltName=DNS:insider-market,IP:127.0.0.1"

ENV LISTEN_HOST=0.0.0.0 \
    LISTEN_PORT=31337 \
    SESSION_TIMEOUT=1200 \
    MAX_CONCURRENT=32 \
    CHALL_DIR=/opt/breach \
    PLAYER_ROOT=/opt/breach/player-root \
    NSJAIL=/usr/local/bin/nsjail

# FLAG must be provided at run time or overridden in challenge.yaml
ENV FLAG="UMDCTF{placeholder_override_in_compose}"

EXPOSE 31337

CMD ["python3", "/opt/breach/infra/supervisor.py"]
