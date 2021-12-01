from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def start():
    return render_template("home.html")

@app.route('/xor_calculator')
def xor_calculator():
    return render_template("calculator.html", calculate_type="xor")

@app.route('/add_calculator')
def add_calculator():
    return render_template("calculator.html", calculate_type="add")

@app.route('/mult_calculator')
def mult_calculator():
    return render_template("calculator.html", calculate_type="mult")

@app.route('/xor', methods=['POST'])
def xor():
    return calculate(0)
    
@app.route('/add', methods=['POST'])
def add():
    return calculate(1)

@app.route('/mult', methods=['POST'])
def mult():
    return calculate(2)


def calculate(operation_index):
    try:
        val1 = request.form['val1']
        val2 = request.form['val2']
        print(val1)
        print(val2)
        print(operation_index)
        if operation_index == 0:
            return str(eval(val1) ^ eval(val2))
        elif operation_index == 1:
            return str(eval(val1) + eval(val2))
        else:
            return str(eval(val1) * eval(val2))
    except Exception as e:
        print(e)
        return "An error occured"