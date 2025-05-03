from flask import *
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "3013fc9e2c055e194f7f6813444aaa14"

CORS(app)

def load_dictionary():
    with open("dictionary.txt", "r") as file:
        return set(word.strip() for word in file.readlines())

valid_words = load_dictionary()

target_word = "FANUM"
grid = [
    ["F", "N", "E", "H", "A"],
    ["A", "K", "E", "L", "B"],
    ["V", "M", "T", "K", "E"],
    ["O", "G", "U", "Y", "U"],
    ["P", "J", "P", "F", "N"]
]

@app.route("/")
def index():
    session["grid"] = [row[:] for row in grid]
    session["moves"] = 0
    session["solved"] = False
    return render_template("index.html", target_word=target_word, grid=grid)

def get_word(g, r1, c1, r2, c2):
    word = []
    if r1 == r2:
        word = g[r1][min(c1, c2):max(c1, c2) + 1]
        if c1 > c2:
            word = word[::-1]
    elif c1 == c2:
        word = [g[r][c1] for r in range(min(r1, r2), max(r1, r2) + 1)]
        if r1 > r2:
            word = word[::-1]
    return word

def check_win(g):
    for i in range(5):
        if "".join(g[i]) == target_word or "".join([r[i] for r in g]) == target_word:
            return True
    return False

@app.route("/move/<r1>-<c1>-<r2>-<c2>")
def move(r1, c1, r2, c2):
    r1 = int(r1)
    c1 = int(c1)
    r2 = int(r2)
    c2 = int(c2)

    if (r1 != r2 and c1 != c2) or session.get("solved"):
        return jsonify({"valid": False})

    if not session.get("grid"):
        session["grid"] = [row[:] for row in grid]

    word = get_word(session["grid"], r1, c1, r2, c2)
    if "".join(word) not in valid_words:
        return jsonify({"valid": False})

    if r1 == r2:
        session["grid"][r1][min(c1, c2):max(c1, c2) + 1] = word[::-1] if c1 < c2 else word
    elif c1 == c2:
        for i, r in enumerate(range(min(r1, r2), max(r1, r2) + 1)):
            session["grid"][r][c1] = word[-i - 1] if r1 < r2 else word[i]
    session["moves"] = (session.get("moves") or 0) + 1

    data = {
        "valid": True,
        "grid": session["grid"],
        "moves": session["moves"]
    }

    if check_win(session["grid"]):
        session["solved"] = True
        data["solved"] = True
        if session["moves"] <= 8:
            data["flag"] = "UMDCTF{spindle_is_the_ultimate_crossover_between_shape_rotators_and_wordcels}"

    return jsonify(data)

if __name__ == "__main__":
    app.run("0.0.0.0", threaded=False, debug=False)
