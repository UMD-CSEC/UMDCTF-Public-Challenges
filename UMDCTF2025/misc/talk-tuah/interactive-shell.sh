#!/bin/bash
RAND="$(tr -dc A-Za-z0-9 </dev/urandom | head -c12)"

# Proof of Work
echo "To connect to this challenge, you need to complete a Proof-of-Work."
echo "Please run the following command to generate a token:"
echo ""
echo "hashcash -mb29 ${RAND}"
echo ""
echo "You can install hashcash from the Ubuntu/Debian repositories, AUR, Homebrew, etc."
echo "Please enter the output of hashcash (just the part after \"hashcash stamp: \") "
read userinput

if ! hashcash -r "${RAND}" -b 29 -d -c "${userinput}"; then
    echo "Proof-of-work was invalid."
    exit 1
fi

mkdir "/tmp/workspaces/${RAND}"
chown user:user "/tmp/workspaces/${RAND}"

echo "A temporary directory has been created for you at /tmp/workspaces/${RAND}"

cgcreate -g "cpu,memory,pids:${RAND}"
cgset -r cpu.max="30000 1000000" "${RAND}"
cgset -r memory.max=10485760 "${RAND}"
cgset -r pids.max=20 "${RAND}"

(sleep 1800 && echo 1 > "/sys/fs/cgroup/${RAND}/cgroup.kill") &

cgexec -g "*:${RAND}" unshare --mount-proc --pid --fork --wd=/app setuidgid user bash -c "sh -i 2>&1"
