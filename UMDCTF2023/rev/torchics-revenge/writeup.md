# Torchic's Revenge Writeup
Torchic struggled with TensorFlow's complex syntax, but after trying PyTorch, it felt like a bird of prey soaring through the sky. It became a PyTorch fanatic, squawking about it like a birdbrain on caffeine.

## Initial Exploration
We're given a large Rust binary. If you managed to get it to run, you would find that it appeared to do nothing but print "poop". Throwing the binary into a decompiler, we see a couple interesting things. One being serde_pickle is called in the main function and another being that it seems we have Rust torch API bindings called tch.

## Pickle
Seeing as there is a call to unpickle and we are not given any files other than the binary, perhaps the pickle is compiled into the binary. That would explain the large size. Running `binwalk` on our binary, we see that the pickle is in fact compiled into the binary. Extracting and unpickling the pickle, it seems there are 10 entries:
```
-rw-r--r-- 1 segal segal 11707920  0
-rw-r--r-- 1 segal segal    27876  1
-rw-r--r-- 1 segal segal 83628000  2
-rw-r--r-- 1 segal segal    12000  3
-rw-r--r-- 1 segal segal 16044000  4
-rw-r--r-- 1 segal segal     5348  5
-rw-r--r-- 1 segal segal 42826784  6
-rw-r--r-- 1 segal segal    32032  7
-rw-r--r-- 1 segal segal  1217216  8
-rw-r--r-- 1 segal segal      152  9
```
 Seeing as this is an ML challenge and we already identify torch API calls, perhaps these are weights and biases. We can observe that odd entries are much smaller. These must be our biases. The larger files must be our weights. Now let's start taking a look back at our decompilation.

 ## Torch
 It looks like we have a `tch::nn::sequential::Sequential` object that we're adding layers to. The first linear layer call is `tch::nn::linear::linear::h16c12570c2c679b9(&var_80, &var_c8, 0x1a4, 0x1b39, &var_118, rbp)`. Those hex values translate to `420` and `6969`, which gives away that these are significant. It seems the input to the layer has size 420 and the output has size 6969. We can do this for all layers to obtain the following structure (represented in PyTorch syntax):
 ```py
 nn.Sequential(
    nn.Linear(420, 6969),
    nn.Linear(6969, 3000),
    nn.Linear(3000, 1337),
    nn.Linear(1337, 8008),
    nn.Linear(8008, 38)
 )
 ```
 We are not done here though. There are also calls to `tch::nn::sequential::Seq...d2df41a6fad4.llvm.8182213912809540348`. They seem to take another function as an argument. Following that linking path, you ultimately get to an activation function. Adding these in, we obtain our complete model:
  ```py
 nn.Sequential(
    nn.Linear(420, 6969),
    nn.ReLU(),
    nn.Linear(6969, 3000),
    nn.Sigmoid(),
    nn.Linear(3000, 1337),
    nn.ReLU(),
    nn.Linear(1337, 8008),
    nn.ReLU(),
    nn.Linear(8008, 38),
    nn.ReLU()
 )
 ```
 We're almost there. Now we need to figure out what the point of this model is. It looks like we have a call to `forward()` on our model:
 
 ```
 var_118 = _$LT$tch..nn..sequential...odule$GT$::forward::hfb6696700d9a15fe(&var_80, &var_68)
 ```

 This references a Tensor object initialized here

 ```
var_68 = tch::wrappers::tensor::Tensor::of_slice::h32bf6ba4c18f7ea0(&data_196030[0x48], 0x1a4)
 ```
0x1a4=420, which is the same size as our input layer. Perfect! We can take the input data from memory. Now we just have to try to run this model with this input data.

## Running
We have everything we need, but we need to combine them correctly. Our weights and biases are in the entries we got from the pickle. If we divide each byte size by 4 for a standard float32 size, we obtain the following sizes:
```
-rw-r--r-- 1 segal segal  2926980  0
-rw-r--r-- 1 segal segal     6969  1
-rw-r--r-- 1 segal segal 20907000  2
-rw-r--r-- 1 segal segal     3000  3
-rw-r--r-- 1 segal segal  4011000  4
-rw-r--r-- 1 segal segal     1337  5
-rw-r--r-- 1 segal segal 10706696  6
-rw-r--r-- 1 segal segal     8008  7
-rw-r--r-- 1 segal segal   304304  8
-rw-r--r-- 1 segal segal       38  9
```
We can see that the bias sizes are the same as our layer sizes output sizes, which makes sense. Additionally, the weight sizes are the same as the each layer input size times the layer output size, which also makes sense, given they are m x n matrices with m = output size and n = input size. Our solve script will simply have to create a sequential model, load the weights and biases, and run the model with our input. This script is left as an exercise to the reader.