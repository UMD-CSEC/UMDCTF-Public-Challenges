from flask import Flask, render_template_string
import requests

app = Flask(__name__)

def get_token():
    r = requests.get('http://maps.ufanet.ru/ufa#1589793911')
    token = r.text.split("Остановка Советская площадь Камера 2")[1]
    token = token.split("marker.token = \'")[1].split('\'')[0]
    return token

def remake_home():
   token = get_token()
   f = open('templates/home.html', 'r')
   stuff = f.read().split('token=')
   f.close()
   first = stuff[0]
   sec = stuff[1].split('\" title=')[1]
   return first + "token=" + token + "\" title=" + sec

@app.route('/')
def home():
    home = remake_home()
    return render_template_string(home)
