#!/bin/sh
cron &
sudo -u web python ./main.py
