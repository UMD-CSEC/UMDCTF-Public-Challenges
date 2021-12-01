from flask import Flask, request, render_template, Response
app = Flask(__name__)

@app.route('/', methods=['GET'])
def start():
    # hack since get accepts head sometimes
    if request.method == "HEAD":
        return real_start()
    return render_template("home.html")

@app.route('/', methods=['HEAD'])
def real_start():
    response = Response()
    response.headers["flag"] = 'UMDCTF-{h3@d1ng_t0w@rd5_th3_l1ght}'
    return response