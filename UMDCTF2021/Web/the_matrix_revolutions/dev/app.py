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
    return "<h2>No one is allowed to enter the matrix now!</h2>"

@app.route('/0')
def m0():
    return "U"

@app.route('/1')
def m1():
    return "M"

@app.route('/2')
def m2():
    return "D"

@app.route('/3')
def m3():
    return "C"

@app.route('/4')
def m4():
    return "T"

@app.route('/5')
def m5():
    return "F"

@app.route('/6')
def m6():
    return "-"

@app.route('/7')
def m7():
    return "{"

@app.route('/8')
def m8():
    return "r"

@app.route('/9')
def m9():
    return "0"

@app.route('/10')
def m10():
    return "b"

@app.route('/11')
def m11():
    return "0"

@app.route('/12')
def m12():
    return "t"

@app.route('/13')
def m13():
    return "5"

@app.route('/14')
def m14():
    return "_"

@app.route('/15')
def m15():
    return "4"

@app.route('/16')
def m16():
    return "3"

@app.route('/17')
def m17():
    return "v"

@app.route('/18')
def m18():
    return "3"

@app.route('/19')
def m19():
    return "r"

@app.route('/20')
def m20():
    return "}"

