import json

def convert_to_ascii(ctext):
        ptext = ''
        for i in range(0, len(ctext), 2):
                d1 = ord(ctext[i]) - 97
                d2 = ord(ctext[i + 1]) - 97
                ptext += chr(d1 * 16 + d2)
        return ptext

def decrypt(ctext):
        f = open('jsondata.json', 'r')
        text = f.read()
        pigpen = json.loads(text)
        inverted_pigpen = {v: k for k, v in pigpen.items()}
        ptext = ''
        for c in ctext.split(" ")[:-1]:
                ptext += inverted_pigpen[c]
        return ptext

f = open('../prod/ciphertext', 'r')
ctext = f.read()
print(convert_to_ascii(decrypt(ctext)))
