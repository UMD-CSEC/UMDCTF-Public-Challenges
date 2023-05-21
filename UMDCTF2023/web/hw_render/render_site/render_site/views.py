from django.http import HttpResponse
import os
import subprocess
import base64

def render(request):
	try:
		base64_latex = request.GET.get('latex')
		bytes_latex = base64.b64decode(base64_latex)
		
		latex_string = bytes_latex.decode('ascii')

		if filter(latex_string):
			return HttpResponse("<h1>Blacklisted latex tags used!</h1>")	

		with open('temp.tex', 'wb') as f:
			f.write(bytes_latex)

		subprocess.run(['pdflatex', '-interaction=nonstopmode', '-no-shell-escape', 'temp.tex'])
		
		if os.path.exists("temp.pdf"):
			with open('temp.pdf', 'rb') as f:
				pdf = f.read()

			response = HttpResponse(content=pdf, content_type='application/pdf')
		else:
			response = HttpResponse("<h1>An error occurred in displaying pdf file.</h1>")
	except:
		purge_temp()
		return HttpResponse("<h1>An error occured in rendering latex.</h1>")

	purge_temp()
	return response

def filter(string):
	string = string.lower()
	blacklisted_commands = ["\\input", "include", "newread", "openin", "file", "read", "closein", "usepackage", "fileline", "verbatiminput", "url", "href", "texttt", "write", "newwrite", "outfile", "closeout", "immediate", "|", "write18", "includegraphics", "openout", "newcommand", "expandafter", "csname", "endcsname"]

	for command in blacklisted_commands:
		if command in string:
			print(command)
			return True

	return False


def purge_temp():
	if os.path.exists("temp.aux"):
		os.remove("temp.aux")

	if os.path.exists("temp.txt"):
		os.remove("temp.txt")

	if os.path.exists("temp.pdf"):
		os.remove("temp.pdf")

	if os.path.exists("temp.tex"):
		os.remove("temp.tex")

	if os.path.exists("temp.log"):
		os.remove("temp.log")
