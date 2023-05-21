"""
A Seq By Any Other Name challenge

Requires participants to make a HTTP GET request for a large file, but the sequence numbers do not increment the same way.
"""
import datetime
import hashlib
import random
import os
import sys


from flask import Flask, render_template, request, session, Response
import lorem
import string
import urllib.request

BASEPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASEPATH, "geneva/"))
# To do traffic modification, leverage geneva
import geneva.engine

app = Flask(__name__)

FLAG = "UMDCTF{a_seq_is_an_ack_if_you_try_hard_enough}"

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main service landing point.
    """

    return render_template("instructions.html")

@app.route("/gimmedafile.txt", methods=["GET", "POST"])
def sendfile():
    """
    Generate a lorem ipsum file at random and calculate the MD5
    """
    def generate():
        s = ""
        for i in range(1000):
            s += lorem.paragraph()
        s += FLAG
        return s.encode()
    return Response(generate(), mimetype='application/octet-stream')



def startup_server():
    """
    Starts up server behind a packet modifier
    """
    port = 80

    adjust_seqs = "[TCP:flags:*]-switch{}-| "\
                  "\/"\
                  "[TCP:flags:*]-switch{}-| "

    with geneva.engine.Engine(port, adjust_seqs, log_level="debug", server_side=True, save_seen_packets=False) as eng:
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


if __name__ == "__main__":
    startup_server()
