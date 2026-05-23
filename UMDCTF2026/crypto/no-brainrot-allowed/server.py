#!/usr/local/bin/python
from Crypto.Util.number import bytes_to_long 
from secret_parameters import d, flag_bytes

# n has been specifically selected to not contain the forbidden two digit sequence.
n = 89496838321330017124211425752928111009238414395285545597372895783391482460166014550795440784240669454038164776392492949832230406030665778241454645944939829559549747525412818621247626093163657213524408194055221128159991890855776297338418179985226639927931716465641085590302394062423554511419578835789906477703 
e = 65537

flag = bytes_to_long(flag_bytes)
assert flag < n
ct = pow(flag, e, n)

print(f"Your flag: {ct}")

print("Send an encrypted message to the UMDCTF organizers!")
print("WARNING: ALL MESSAGES WILL BE SCANNED FOR SIGNS OF POTENTIAL BRAINROT ACTIVITY.")

while True:
    user_inputs = input("Your messages: ").split(',')
    for user_ct in user_inputs:
        user_ct = int(user_ct)
        if user_ct >= n or user_ct < 0:
            print("Erm that's not a valid message")
            exit()

        pt = hex(pow(user_ct, d, n))

        if pt.startswith("0x67"):
            print("ERROR: BRAINROT DETECTED. THIS INCIDENT WILL BE REPORTED.")
        else:
            print("The UMDCTF team thanks you for your message!")
        print()
