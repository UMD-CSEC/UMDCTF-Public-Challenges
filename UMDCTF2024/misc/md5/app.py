from flask import *
from flask_cors import CORS
import hashlib
import requests


app = Flask(__name__)
app.secret_key = "ny398vtywoieyuglsifvyvhglawchrgliusfdnhgljhgl"

CORS(app)


@app.route("/")
def index():
    return render_template("./index.html")


@app.route("/submit")
def submit():
    m = request.args.get("input")
    h = hashlib.md5(m.encode()).hexdigest()

    if h == "826f550caf7b1f9e9026619ef6910410":
        requests.post(
            "https://discord.com/api/webhooks/1233351564307988555/Ufu7dgXRiLbOTEe0nHtesIE3vcXo_SZ15YnIKf1u5LDXKiY9BYyGWepclmzFpY0N-nCD",
            json={"content": m, "attachments": [], "embeds": None},
        )
        session["solved"] = True
        return redirect("/win")

    flash("incorrect", "error")
    return redirect("/")


@app.route("/win")
def win():
    if session.get("solved"):
        return render_template("win.html")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run("0.0.0.0", threaded=False, debug=False)
