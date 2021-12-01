from flask import Flask, request, jsonify, session, Response, render_template, url_for
from flask_cors import CORS, cross_origin
import base64
import random
import re
import mysql.connector
import sys
app = Flask(__name__)
app.secret_key = "UMDCTF-2019"
app.config['SESSION_COOKIE_HTTPONLY'] = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

config = {
    'user': 'root',
    'password': 'UMD_CTF_DB_PW',
    'host': 'db',
    'port': '3306',
    'database': "umdctf"
}

def userAgentFilter(value):
    pattern = re.compile("sqlmap")
    if (pattern.search(value)):
        return True
    return False
def filterBadWords(value):
    blacklist = set(["-", ";"])
    value = ''.join([c for c in value if c not in blacklist])
    or_pattern = re.compile(" or ", re.IGNORECASE)
    and_pattern = re.compile(" and ", re.IGNORECASE)
    sleep_pattern = re.compile(" sleep ", re.IGNORECASE) 
    order_pattern = re.compile(" order ", re.IGNORECASE)
    where_pattern = re.compile(" where ", re.IGNORECASE)
    by_pattern = re.compile(" by ", re.IGNORECASE)

    value = or_pattern.sub("", value)
    value = and_pattern.sub("", value)
    value = sleep_pattern.sub("", value)
    value = order_pattern.sub("", value)
    value = by_pattern.sub("", value)
    value = where_pattern.sub("", value)
    return value
    
def authenticated():
    rv = []
    session_token = session['user']
    print(session['user'])
    # "admin", "71aaf9698acfcdeb382bac8de0406ea8e8561d60455af041", "umd")
    db = mysql.connector.connect(**config)
    # db = pymysql.connect(db_host, db_user, db_password, database)
    cur = db.cursor(prepared=True)

    query = """SELECT username FROM sessions WHERE session_token = %s"""
    cur.execute(query, (session_token,))

    u = [x for x in cur]

    try:
        cur.execute("SELECT * FROM users WHERE username = '" +
                    str(u[0][0]) + "';")
    except:
        return {}
    for row in cur.fetchall():
        rv.append(row)
    if len(rv) > 0:
        return rv[0][0]
    else:
        return {}


@app.route('/api/authenticate', methods=["POST", "OPTIONS"])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def verify():
    if request.method == "OPTIONS":
        resp = Response()
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        return resp
    else:
        counter = 0
        if(userAgentFilter(request.headers.get('User-Agent'))):
            return "-1"
        else:
            rv = []
            theHash = b''
            username = request.form['username']
            password = request.form['password']
            if len(username) < 4 or len(password) < 4:
                return "-1"
            else:

                username = filterBadWords(username)
                password = filterBadWords(password)

                db = mysql.connector.connect(**config)

                cur = db.cursor()

                cur.execute("SELECT * FROM users WHERE username = '" +
                            str(username) + "' AND password = '" + str(password) + "';")
                cur.fetchall()
                print(password)
                if (cur.rowcount > 0):
                    print("Send Flag")

                    theHash = base64.b64encode(b'UMDCTF-{84y_w425_3p150d33_23v3n93_0f_7h3_f149_84y}').decode('utf-8')
                else: 
                    print("reached")

                    theHash = "-1"
                cur.close()
                return theHash

@app.route('/')
def index():
    return render_template('index.html')


app.run(host="0.0.0.0")
