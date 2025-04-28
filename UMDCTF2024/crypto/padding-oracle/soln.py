from padding_oracle import check_ct
from Crypto.Random import get_random_bytes



# Finds str1^str2 
def xor(str1,str2):

    xored = bytes(a ^ b for a, b in zip(bytes.fromhex(str1), bytes.fromhex(str2)))
    xored_str = xored.hex()
   
    return xored_str


def unpad(block):
    
    last_byte = block[-2:]
    num_padding = int(last_byte,16)
    
    return block[:-2*num_padding]

def attack_block(ct1,ct2):

    I_block2 = '' # intermediate step
    P_block2 = '' # plaintext block2
    ct_block1 = ct1
    ct_block2 = ct2

    for i in range(0,16):
        
        i1 = 16-i-1 # block starting byte
        i2 = 16-i # block ending byte
        
        padding_byte = ('0' if i+1 < 0x10 else '')+hex(i+1)[2:]
        padding_block2 = padding_byte*(i+1)
    
        # trying different bytes
        for j in range(0x000,0x100):
            
            prefix = get_random_bytes(i1).hex() 
            attempt = ('0' if j < 0x10 else '')+hex(j)[2:] 
            suffix = xor(I_block2,padding_block2[2:])

            ctp_block1 = prefix+attempt+suffix
            ctp = ctp_block1+ct_block2
            
            if check_ct(ctp):

                I_byte = xor(padding_byte,attempt)
                I_block2 = I_byte+I_block2

                P_byte = xor(ct1[2*i1:2*i2],I_byte)
                P_block2 = P_byte+P_block2

                break

    return P_block2

def attack(iv,ct):
 
    pt = ''

    for i in range(len(ct)-2*16,-1,-2*16):
       
        i1 = i-2*16
        i2 = i
        i3 = i+2*16
      
        block1 = iv if i1 < 0 else ct[i1:i2]
        block2 = ct[i2:i3]

        pt = attack_block(block1,block2)+pt

    pt = unpad(pt)
    pt = bytes.fromhex(pt).decode()
    return pt
        
   
fp1 = open('flag.txt','r')
ct = fp1.read()
fp1.close()
fp2 = open('iv.txt','r')
iv = fp2.read()
fp2.close()
print(attack(iv,ct))