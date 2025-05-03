#!/usr/local/bin/python
f = open('flag.txt').read()

target = 'SIGMA'

while True:
    guess = input("Guess: ")
    if len(guess) != 5:
        print("Invalid guess.")
        continue
    for j in range(5):
        if target[j] == guess[j]:
            print('🟩', end='')
        elif guess[j] in target[j]:
            print('🟨', end='')
        else:
            print('⬛', end='')
    print('')
    try:
        exec(guess)
        print('🟩🟩🟩🟩🟩')
    except:
        print("🟥🟥🟥🟥🟥")
