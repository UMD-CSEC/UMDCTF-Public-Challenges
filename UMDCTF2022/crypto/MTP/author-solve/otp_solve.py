from binascii import hexlify, unhexlify
import hashlib

def space_method(ciphertexts, plaintexts):
    for k in range(0, len(ciphertexts[0])-1, 2):
        for i in range(len(ciphertexts)):
            c1 = ciphertexts[i].lower()
            byte1 = c1[k:k+2]
            possible_spaces = {} 

            for j in range(0, len(ciphertexts)):
                c2 = ciphertexts[j].lower()
                byte2 = c2[k:k+2]
           
                xord_orig = int(byte1, 16) ^ int(byte2, 16)
                xord = bin(xord_orig)[2:]
                xord2 = '0'*(8-len(xord)) + xord
                if xord2[0:2] == '01': # one of these is a space
                    if len(possible_spaces.keys()) > 0 and i in possible_spaces.keys():
                        possible_spaces[i][j] = xord_orig
                    else:
                        possible_spaces[i] = {j: xord_orig}
                    
                    if len(possible_spaces.keys()) > 0 and j in possible_spaces.keys():
                        possible_spaces[j][i] = xord_orig
                    else:
                        possible_spaces[j] = {i: xord_orig}

            for z in range(8):
                if z in possible_spaces.keys() and len(possible_spaces[z].keys()) > 3: # we know this exact character is a SPACE
                    plaintexts[z][k//2] = ' '
                    for ke, v in possible_spaces[z].items():
                        plaintexts[ke][k//2] = chr(v ^ 0x20)
    
            #print(f'possible spaces for byte {k//2}: {possible_spaces}') 
   
    #print('\n\n')
    return plaintexts

def known_char_method(ciphertext, plaintexts, known_chars):
    for k,v in known_chars.items():
        for ct, letter in v.items():
            for i in range(8):
                if i != ct:
                    byte1 = ciphertext[i].lower()[2*k:(2*k)+2]
                    byte2 = ciphertext[ct].lower()[2*k:(2*k)+2]
                    plaintexts[i][k] = chr(ord(letter) ^ int(byte1, 16) ^ int(byte2, 16))
            plaintexts[ct][k] = letter

    return plaintexts

if __name__ == '__main__':
    plaintexts = []
    for _ in range(8):
    	plaintexts.append(list('_'*30))
    
    with open('ciphertexts.txt', 'r') as f:
        ciphertexts = f.read().strip().split('\n')
        #print('\n'.join(ciphertexts) + '\n') 
    
    plaintexts2 = space_method(ciphertexts, plaintexts)
    for p in plaintexts2:
        print(''.join(p))

    print('\n')
    #known_chars = {6: {4: 's'}}
    known_chars = {0: {0: 'C'}, 11: {0: 't'}, 12: {3: ' '}, 19: {3: 'e'}, 20: {3: 't'}, 21: {0: ' '}, 22: {2: ' '}, 23: {0: 'h'}, 28: {0: 'r'}, 29: {0: '.'}} 

    plaintexts3 = known_char_method(ciphertexts, plaintexts2, known_chars)
    pt_str = ''
    for p in plaintexts3:
        pt_str += ''.join(p)
        print(''.join(p))

    print('\nUMDCTF{' + hashlib.md5(pt_str.encode()).hexdigest() + '}')

