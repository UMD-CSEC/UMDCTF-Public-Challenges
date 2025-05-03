#!/bin/bash
rm -rf /tmp/talk_tuah
mkdir /tmp/talk_tuah
chown flag:flag /tmp/talk_tuah
chmod a-r /tmp/talk_tuah

rm -rf /tmp/workspaces
mkdir /tmp/workspaces
chown root:root /tmp/workspaces
chmod a-r /tmp/workspaces

chmod o-w /tmp

socat TCP-LISTEN:1447,fork EXEC:/interactive-shell.sh
