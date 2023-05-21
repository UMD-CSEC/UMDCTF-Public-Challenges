# Elgyem's Password Writeup
Elgyem input the password to his UFO into a neural network, but sadly he lost the password. All he has left are the network and the output. Can you help Elgyem fly back home?

## Initial Background
Looking into how neural networks work, you will find that they are essentially just matrix operations, where the computation of each layer is of the form $\mathbf{y}=z(W\mathbf{x}+\mathbf{b})$, with $z$ being our activation function, $W$ being a matrix of weights, $\mathbf{x}$ being the input vector, and $\mathbf{b}$ being the bias vector. Conveniently, for this challenge, the provided model (in model.py) has no activation functions; it is just a series of linear layers. This means we can simply represent each layer in the form $\mathbf{y}=W\mathbf{x} + \mathbf{b}$.

## Note on Reduction of our Network
Before we move on to solve paths, it is important to note that given that our network has no activation functions (or perhaps technically exclusively linear activation functions), we can actually reduce the entire multilayer architecture into a single layer. Consider a network of 3 layers (excluding the input layer, which does no computation). We represent this network's computation as $\mathbf{y} = A_3(A_2(A_1\mathbf{x}+\mathbf{b}_1)+\mathbf{b}_2)+\mathbf{b}_3$. Expanding (since matrix multiplication is distributive), we have $\mathbf{y}=A_3A_2A_1\mathbf{x}+A_3A_2\mathbf{b}_1+A_3\mathbf{b}_2+\mathbf{b}_3$. Only the first term of this sum is depends on $\mathbf{x}$, our input vector, so we obtain that our new weight matrix $W=A_3A_2A_1$ and the remaining terms are our new bias, namely $\mathbf{b}=A_3A_2\mathbf{b}_1+A_3\mathbf{b}_2+\mathbf{b}_3$. We have now successfuly reduced our multilayer network down to one layer with $\mathbf{y}=W\mathbf{x}+\mathbf{b}$. This can be applied to any number of layers, provided they have exclusively linear activation functions.

## Considering Inversion
Now, with some knowledge of linear algebra, one would perhaps think of inverting a layer by doing something like $\mathbf{x}=W^{-1}(\mathbf{y}-\mathbf{b})$. Here we run into our first issue. Since all adjacent layers are of different dimensions, none of our layers have square weight matrices, and thus these weight matrices are not invertible. We can solve this issue by using the [Moore-Penrose inverse](https://en.wikipedia.org/wiki/Moore%E2%80%93Penrose_inverse) of the form $A^+=(A^TA)^{-1}A^T$. At first glance, these seems like it might work. However, it won't. The reason for this is that our matrix multiplication $A\mathbf{x}$ is not necessarily [injective](https://en.wikipedia.org/wiki/Injective_function), meaning that there would not necessarily be a single unique solution for the initial vector. In the case of this challenge, there are in fact multiple initial vectors that produce the given output vector, so this approach will not work. To look more into this, see [this StackExchange answer](https://math.stackexchange.com/a/2199729). If you calculate the dimension of the kernel of our combined weight matrix in this case, you will find it is nonzero, and thus our mapping is not injective.

## Considering an ML-based Optimization
So the inversion idea isn't going to work. We need another idea. While I was handling tickets for this challenge, I saw some people consider writing a ML-based optimization algorithm to obtain the input vector that mapped to the given output vector. Initially, this fails for essentially the same reason that the inversion idea failed: there are multiple input vectors that produce the given output vector. However, you can integrate the `UMDCTF{}` flag format into your loss function, which would theoretically solve this issue. However, I don't think this is a very time-efficient solution. While it theoretically could work, and would be a very cool solution, it would take a lot of tinkering around with parameters and loss functions. And plus it isn't really making use of the mathematically exact values provided in the model and outputs.

## A Good Solution
So we want a better solution that also utilizes these beautiful mathematically exact values we're given. Z3 is great for this (Sage also works, but my official solution uses Z3). We can write a Z3 script that has 22 initial unknown values, and then performs the network computation on them using the weights given. Assuming our input vector is ASCII values, we can constrain our inputs to integers. We can also constrain to the flag format. This is enough to obtain a solution with Z3. Below is a solve script that does not utilize reduction of our network to one single computational layer. Sidenote: this script uses like 31GB of RAM on my system. It is much more efficient to utilize reduction of the network.
```py
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
```