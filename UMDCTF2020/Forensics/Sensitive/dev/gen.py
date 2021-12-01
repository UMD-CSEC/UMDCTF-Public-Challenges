f = open('original','rb')
x = f.read()
f.close()


a = open('new','ab')
for i in range(len(x)):
	a.write(x[i])
	a.write(b' ')

a.close()
