from z3 import *

layers = [[[], []]]
data = open("./model.txt", "r").readlines()
biases = False
for l in data:
    l = l.strip()
    if "layer" in l:
        i = int(l[-1])
        layers.append([[], []])
    elif "biases" in l:
        biases = True
    elif "weights" in l:
        biases = False
    elif len(l) > 0:
        nums = [RealVal(x) for x in l.split(" ")]
        if biases:
            layers[i][1] += nums
        else:
            layers[i][0] += nums

layer_data = [[]]
for i in range(22): # input layer size
    layer_data[0].append(Int(str(i)))
for i in range(1, len(layers)):
    layer_data.append([])
    for j in range(len(layers[i][1])):
        n = RealVal(0)
        for k in range(len(layer_data[i - 1])):
            n += layer_data[i - 1][k] * layers[i][0][j * len(layer_data[i - 1]) + k]
        n += layers[i][1][j]
        layer_data[-1].append(n)

outputs = [RealVal(x) for x in open("./outputs.txt").read().strip().split(" ")]
s = Solver()
for i in range(len(layer_data[-1])):
    s.add(layer_data[-1][i] == outputs[i])
for i in layer_data[0]:
    s.add(i > RealVal(32))
    s.add(i < RealVal(128))

flag_header = [85,77,68,67,84,70,123] # UMDCTF{
for i in range(len(flag_header)):
    s.add(layer_data[0][i] == RealVal(flag_header[i]))

s.check()
print(s.model())