from binascii import hexlify, unhexlify
from string import ascii_lowercase

def decrypt(ct, key):
    pt = ''
    for i in range(len(ct)):
        pt += chr(ct[i] ^ key[i%len(key)])
    return pt

def find_key(ct, key_len):
    # using key length, find the key
    arr = [(ct[i:i+key_len]) for i in range(0, len(ct), key_len)]
    arr = arr[:-1]
    key = []
    for i in range(key_len):
        text = []
        for g in arr:
            text.append(g[i])

        pos_keyi = []
        for k in range(256):
            new_text = [(text[c] ^ k) for c in range(len(text))]
            old = new_text
            new_text.sort()
            charrs = ''.join([chr(text[c] ^ k) for c in range(len(text))])
            
            count = 0
            for c in charrs:
                if c in ascii_lowercase:
                    count += 1
            
            if ((new_text[0] > 31) and (new_text[0] < 127)) and ((new_text[-1] > 31) and (new_text[-1] < 127)) and (charrs.count(' ') > 10) and (count/len(new_text) > 0.5):
                #print(''.join([chr(int(i)) for i in old]))
                pos_keyi.append(k)

        key.append(pos_keyi)
    
    print(key) 
    key = [k[0] for k in key]
    return key

def find_key_length_ic(ct):
    # index of coincidence to find key length
    delt_ic_arr = []
    for k_len in range(1,255):
        arr = [(ct[i:i+k_len]) for i in range(0, len(ct), k_len)]
        #print(f'trying k_len = {k_len}')
        delt_ic = get_delta_ic(arr, len(ct))
        delt_ic_arr.append(delt_ic)
        print(f'k_len = {k_len} --- delt_ic = {delt_ic}')
        #break

    curr_best_diff = 10000000
    curr_best_index = 2
    for i in range(2 ,len(delt_ic_arr)):
        d_ic = delt_ic_arr[i]
        if (abs(d_ic - 0.0686) < curr_best_diff) and (not ((i+1)/curr_best_index).is_integer()):
            curr_best_diff = abs(d_ic - 0.0686)
            curr_best_index = i + 1 # key length can't be 0

    key_len = curr_best_index
    print(f'\n*** The key length is most likely {key_len} based on the full ASCII 7-bit spectrum ***\n') 
    return key_len

def get_delta_ic(groups, t):
    text = []
    for g in groups[:-1]:
        text.append(g[0])

    looked = []
    delt_ic = 0
    for c in text:
        if c not in looked:
            cnt = text.count(c)
            delt_ic += ((cnt)*(cnt-1))
            looked.append(c) 

    delt_ic /= (len(text) * (len(text) - 1))
    #delt_ic *= len(looked)

    return delt_ic

def main():
    # Open ciphertext fil and convert to bytes
    with open('ciphertext.txt', 'r') as f:
        ct = f.read()
        ct = unhexlify(ct.strip())

    print(len(ct))
    key_len = find_key_length_ic(ct)
    key = find_key(ct, key_len)
    if len(key) == key_len:
        pt = decrypt(ct, key)
        key = ''.join([hex(k)[2:] for k in key])
        print(f'key = {key}\nplaintext = {pt}')

if __name__ == '__main__':
    main()
