from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/the-matrix')
def thematrix():
    user_agent = request.headers.get('User-Agent')
    if "bot" in user_agent or "Bot" in user_agent:
        return render_template('the-matrix.html')
    else:
        return redirect('/403', code=303)

@app.route('/403')
def four_zero_three():
    return "<h2>This page is for robots only, you are not allowed to access this content!</h2>"
