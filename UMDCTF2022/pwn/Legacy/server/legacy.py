#!/usr/bin/env python2.7
#This challenge must be run on Python 2.7
#This file should not be visible to the CTFers
import random
secret = random.randrange(0,1000000000000000514)
with open('flag.txt', 'r') as f:
  flag = f.readlines()[0]
print("I bet you can't guess my *secret* number!")
print("I'll give you hint, its between 0 and 0,1000000000000000514!")
solved = False
for i in range(3):
	if (input(str(3-i) + " chances left! \n") == secret):
		print("No way!")
		print(flag)
		solved = True
		break
if solved == False:
	print("Deprecated shmeprecated!")
	print("Python 2 will never die!")