from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        ticket = random.randrange(1, 1001, 1)
        return redirect("/ticket?num=" + str(ticket))
    return render_template("index.html")


@app.route("/ticket")
def ticket():
    if "num" in request.args:
        num = request.args["num"]
        if num == "0":
            return render_template("flag.html")
        else:
            return render_template("ticket.html", ticket=num)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
