from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import os
import re
import random
import string
from werkzeug.utils import secure_filename
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['MAX_CONTENT_LENGTH'] = 1000

# Directory to save uploaded files and images
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_uploads_dir(d=None):
    dirname = os.path.join(UPLOAD_FOLDER, ''.join(random.choices(string.ascii_letters, k=30)))
    if d is not None:
        dirname = d
    session['upload_dir'] = dirname
    os.mkdir(dirname)
    os.popen(f'cp flag.txt {dirname}')
    os.popen(f'cp basedict.brainrot {dirname}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'user_file' not in request.files:
            return render_template('index.html', error="L + RATIO + YOU FELL OFF")
        user_file = request.files['user_file']
        if not user_file.filename.endswith('.brainrot'):
            return render_template('index.html', error="sorry bruv that aint brainrotted enough")
        if 'upload_dir' not in session:
            create_uploads_dir()
        elif not os.path.isdir(session['upload_dir']):
            create_uploads_dir(session['upload_dir'])
        fname = unquote(user_file.filename)
        if '/' in fname:
            return render_template("index.html", error="dont do that")
        user_file.save(os.path.join(session['upload_dir'], fname))
        return redirect(url_for('dict'))
    return render_template('index.html')

@app.route('/dict')
def dict():
    if 'upload_dir' not in session:
        create_uploads_dir()
    elif not os.path.isdir(session['upload_dir']):
        create_uploads_dir(session['upload_dir'])

    cmd = f"find {session['upload_dir']} -name \\*.brainrot | xargs sort | uniq"
    results = os.popen(cmd).read()
    return render_template('dict.html', results=results.splitlines())



if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
