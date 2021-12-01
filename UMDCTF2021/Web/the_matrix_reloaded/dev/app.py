from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/the-matrix', methods=['GET'])
def the_matrix():
    languages = [lang for lang in request.accept_languages.values()]
    languages_str = "".join(languages)
    if "is" in languages_str.lower():
        return render_template('the-matrix.html')
    return "<h2>This page is for robots only, you are not allowed to access this content!</h2>"
