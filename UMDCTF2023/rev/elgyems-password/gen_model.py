import math
import random

random.seed(69420)

def gen_num():
    return str(math.floor((random.random() - 0.5) * 4000)) + "/1000"

layers = [22, 69, 420, 800, 85, 13, 37]

output = ""

for i in range(1, len(layers)):
    output += "layer" + str(i) + "\n"
    output += "biases\n"
    biases = []
    for _ in range(layers[i]): # biases
        biases.append(gen_num())
    output += " ".join(biases) + "\n"
    output += "weights\n"
    for _ in range(layers[i]): # weights
        weights = []
        for _ in range(layers[i - 1]):
            weights.append(gen_num())
        output += " ".join(weights) + "\n"

with open("model.txt", "w") as f:
    f.write(output)