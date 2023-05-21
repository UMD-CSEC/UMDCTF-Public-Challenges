MORSE_CODE_DICT = { 'a':'.-', 'b':'-...',
                    'c':'-.-.', 'd':'-..', 'e':'.',
                    'f':'..-.', 'g':'--.', 'h':'....',
                    'i':'..', 'j':'.---', 'k':'-.-',
                    'l':'.-..', 'm':'--', 'n':'-.',
                    'o':'---', 'p':'.--.', 'q':'--.-',
                    'r':'.-.', 's':'...', 't':'-',
                    'u':'..-', 'v':'...-', 'w':'.--',
                    'z':'-..-', 'y':'-.--', 'z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

def encrypt(message):

    cipher = ''
    for letter in message:
        if letter != ' ':
 
            # Looks up the dictionary and adds the
            # corresponding morse code
            # along with a space to separate
            # morse codes for different characters
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            # 1 space indicates different characters
            # and 2 indicates different words
            cipher += ' '
 
    
    return cipher
 
def decrypt(message):

    pt = ''

    words = message.split("  ")
    words2 = []

    for word in words:
        words2+=[word.split(' ')]

    for word in words2:
        for letter in word:

            if len(letter) > 0:
                c = [key for key in MORSE_CODE_DICT if (MORSE_CODE_DICT[key] == letter)][0]
                pt+=c

        pt+=' '

    return pt



def textify(message):

    textify = ''

    txt = 'go catch the bug paras! abra likes his speed! go catch zubat or not! like paras cute zubat is fun! hes great! go catch rock onix! onix loves my new matte rocks lol!'

    for i in range(0,len(message)):

        if message[i] == '-':

            textify+=txt[i].capitalize()

        elif message[i] == '.':

            textify+=txt[i].lower()
        
        else:
            
            textify+=txt[i]

    return textify

def untextify(message):

    morse = ''
    for i in range (0,len(message)):

        if message[i] == '!':
            
            morse+=' '

        elif message[i] == ' ':
            
            if not message[i-1] == '!':

                morse+=' '
        
        else:

            if message[i].capitalize() == message[i]:
                morse+='-'

            else:

                morse+='.'

    return morse

msg = 'm0rs3 c0d3 m34ns h4v1ng s0 m8ch f8ns13s'

ct1 = encrypt(msg)
ct2 = textify(ct1)
print(ct2)

pt1 = untextify(ct2)
print(decrypt(ct1))
