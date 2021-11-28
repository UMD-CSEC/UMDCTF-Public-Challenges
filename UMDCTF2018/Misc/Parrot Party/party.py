from flask import Flask, Response
from colorama import init, Fore, Style

init()

import random
import time
import sys

app = Flask(__name__)

a = [
    'BLACK', 'BLUE', 'CYAN', 'GREEN', 'LIGHTBLACK_EX', 'LIGHTBLUE_EX', 'LIGHTCYAN_EX',
    'LIGHTGREEN_EX', 'LIGHTMAGENTA_EX', 'LIGHTRED_EX', 'LIGHTWHITE_EX', 'LIGHTYELLOW_EX',
    'MAGENTA', 'RED', 'RESET', 'WHITE', 'YELLOW'
]

f = [open(f"frames/{i}.txt").read().replace('\'', '.') for i in range(10)]


@app.route('/')
def index():
    def g():
        for c in f:
            d = random.choice(a)
            ca = getattr(Fore, d)
            c = ca + c
            print(c)
            yield """
{c}
""".format(c=c) + Style.RESET_ALL
            time.sleep(0.07)  # an artificial delay

    return Response(g())


if __name__ == "__main__":
    app.run(host='localhost', port=23423, debug=True)