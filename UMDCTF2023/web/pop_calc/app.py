#!/usr/bin/env python3

import flask


app = flask.Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        return flask.render_template("index.html")

    if flask.request.method == "POST":
        provided = flask.request.form["calc"]
        if "calc" in flask.request.form:
            try:
                print(provided)
                calculated = safe_math_eval(provided)
                return str(calculated)
            except:
                return "[ERROR] " + flask.render_template_string(provided)
    return provided


def safe_math_eval(string):
    allowed_chars = "0123456789+-*./"
    for char in string:
        if char not in allowed_chars:
            raise Exception("Unsafe eval")

    return eval(string, {"__builtins__": None}, {})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
