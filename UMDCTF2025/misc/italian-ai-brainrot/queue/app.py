from flask import Flask, render_template, request
import pickle
import socket

app = Flask(__name__)

def send_to_runner(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("runner", 6967))
            sock.send(pickle.dumps(data))
            response = sock.recv(1024)
            return response
    except Exception as e:
        return f"error: failed to connect: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    if not data or "bytes" not in data:
        return "error: missing bytes in json", 400

    try:
        state_bytes = list(map(int, data["bytes"]))
        for b in state_bytes:
            if b < 0 or b > 255:
                raise ValueError("invalid byte value")
    except Exception as e:
        return f"error: invalid input: {e}", 400

    return send_to_runner(state_bytes)

@app.route("/status/<token>", methods=["GET"])
def check_status(token):
    return send_to_runner(token)

if __name__ == "__main__":
    app.run("0.0.0.0", threaded=False, debug=False)
