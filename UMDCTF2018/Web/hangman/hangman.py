import random

from jinja2 import Environment
import flask
from flask_sqlalchemy import SQLAlchemy

global app
app = flask.Flask(__name__)
app.flag = "UMDCTF-{hows-it-hanging}"

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

env = Environment()


def random_pk():
    return random.randint(1e9, 1e10)


def random_word():
    words = [line.strip() for line in open('words.txt')]
    return random.choice(words).upper()


class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))

    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        a = env.from_string(self.tried, globals=globals()).render()
        print(a)
        return a

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        return 100 + 2 * len(set(self.word)) + len(self.word) - 10 * len(self.errors)

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += " " + letter
            db.session.commit()

    # Game status

    @property
    def won(self):
        return self.current == self.word

    @property
    def lost(self):
        return False

    @property
    def finished(self):
        return self.won or self.lost


# Controller


@app.route('/')
def home():
    games = sorted(
        [game for game in Game.query.all() if game.won], key=lambda game: -game.points)[:10]
    return flask.render_template('home.html', games=games)


@app.route('/play')
def new_game():
    player = flask.request.args.get('player')
    game = Game(player)
    db.session.add(game)
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))


@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        letter = flask.request.form['letter']
        if letter:
            game.try_letter(letter)

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current, errors=game.errors, finished=game.finished)
    else:
        return flask.render_template('play.html', game=game)


# Main

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
