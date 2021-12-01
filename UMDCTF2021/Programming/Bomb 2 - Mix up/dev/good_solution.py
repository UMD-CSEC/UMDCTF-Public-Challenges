from pwn import *

def find_mode(part):
    lib = {}
    for char in part:
        if char not in lib.keys():
            lib[char] = 1
        else:
            lib[char] += 1

    maxx = 0
    max_char = ''
    for k in lib.keys():
        if lib[k] > maxx:
            max_char = k
            maxx = lib[k]

    return max_char


host = '157.230.221.9'
port = 6000
r = remote(host, port) 

print(r.recv().decode())
r.sendline(b'')

total = ""
data = r.recv().decode()
while "Code" not in data:
    total += data
    data = r.recv().decode()
total = total.split('\n')
#print(total)

code = ""
for part in total[:-1]:
    mode = find_mode(part)
    code += mode

r.sendline(code.encode())
print(r.recv().decode())
print(code)
