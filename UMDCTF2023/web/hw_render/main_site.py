from flask import Flask, request, Response, render_template
from werkzeug.datastructures import ImmutableMultiDict
import base64
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
   return render_template('index.html')

@app.route('/render', methods=['GET'])
def render():
	base64_latex = request.args.get('latex')
	if base64_latex == None:
		return "<h1>Please enter some latex.</h1>"
	else:
		try:
			bytes_latex = base64.b64decode(base64_latex)
			latex_string = bytes_latex.decode('ascii')

			if filter(latex_string):
				return "<h1>Unsafe latex tags used!</h1>"			
			else:
				response = requests.get("http://localhost:8000/render", params=request.args.to_dict(flat=False))
				return Response(response.content, content_type=response.headers['Content-Type'])
		except:
			return "<h1>Error in processing request</h1>"

@app.route('/robots.txt', methods=['GET'])
def robots_txt():
	return Response("User-agent: *\r\nDisallow: /app/flag\r\n", content_type='text/plain')


def filter(string):
	string = string.lower()
	blacklisted_commands = ["input", "include", "newread", "openin", "file", "read", "closein", "usepackage", "fileline", "verbatiminput", "url", "href", "texttt", "write", "newwrite", "outfile", "closeout", "immediate", "|", "write18", "includegraphics", "openout", "def", "catcode", "newcommand", "expandafter", "csname", "endcsname"]

	for command in blacklisted_commands:
		if command in string:
			return True

	return False


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=4433)
