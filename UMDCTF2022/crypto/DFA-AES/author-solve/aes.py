#OSC483
# Joey Lemon - 09/11/2021

# Non-linear substitution table used in several byte substitution
# transformations
# and in the Key Expansion routine to perform a one for-one substitution of a
# byte value.
s_box = (
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16)

inv_s_box = (
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d)

# Round constant word array for usage in the key expansion routine
r_con = (
    0x00000000, 0x01000000, 0x02000000, 0x04000000,
    0x08000000, 0x10000000, 0x20000000, 0x40000000,
    0x80000000, 0x1B000000, 0x36000000, 0x6C000000,
    0xD8000000, 0xAB000000, 0x4D000000, 0x9A000000,
    0x2F000000, 0x5E000000, 0xBC000000, 0x63000000,
    0xC6000000, 0x97000000, 0x35000000, 0x6A000000,
    0xD4000000, 0xB3000000, 0x7D000000, 0xFA000000,
    0xEF000000, 0xC5000000, 0x91000000, 0x39000000,
    0x72000000, 0xE4000000, 0xD3000000, 0xBD000000,
    0x61000000, 0xC2000000, 0x9F000000, 0x25000000,
    0x4A000000, 0x94000000, 0x33000000, 0x66000000,
    0xCC000000, 0x83000000, 0x1D000000, 0x3A000000,
    0x74000000, 0xE8000000, 0xCB000000, 0x8D000000
)

# Matrix for fixed polynomial a(x) for use in the mix_columns() function
ax = [[0x02, 0x03, 0x01, 0x01],
      [0x01, 0x02, 0x03, 0x01],
      [0x01, 0x01, 0x02, 0x03],
      [0x03, 0x01, 0x01, 0x02]]

inv_ax = [[0x0e, 0x0b, 0x0d, 0x09],
          [0x09, 0x0e, 0x0b, 0x0d],
          [0x0d, 0x09, 0x0e, 0x0b],
          [0x0b, 0x0d, 0x09, 0x0e]]


def encrypt(plaintext, key, verbose=False):
    """
    Perform the AES cipher routine on the given plaintext using the given key.
    Specify verbose mode to print out each step of the routine.
    """
    Nb = 4
    Nk = int((len(key) * 4) / 32)
    Nr = Nk + 6
    w = key_expansion(text_to_bytes(key), Nb, Nr, Nk)
    state = text_to_matrix(plaintext)

    print_round(0, 'input', matrix_to_text(state), verbose)
    add_round_key(state, w, 0, Nb)
    print_round(0, 'k_sch', get_round_key(w, 0, Nb), verbose)

    for round in range(1, Nr + 1):
        print_round(round, 'start', matrix_to_text(state), verbose)

        sub_bytes(state)
        print_round(round, 's_box', matrix_to_text(state), verbose)

        shift_rows(state)
        print_round(round, 's_row', matrix_to_text(state), verbose)

        if round != Nr:
            mix_columns(state)
            print_round(round, 'm_col', matrix_to_text(state), verbose)

        add_round_key(state, w, round, Nb)
        print_round(round, 'k_sch', get_round_key(w, round, Nb), verbose)

    #print_round(round, 'output', matrix_to_text(state), True)
    print(f'ct: {matrix_to_text(state)}')

    return matrix_to_text(state)

def encrypt_inject(plaintext, key, bit, verbose=False):
    """
    Perform the AES cipher routine on the given plaintext using the given key.
    Specify verbose mode to print out each step of the routine.
    """
    Nb = 4
    Nk = int((len(key) * 4) / 32)
    Nr = Nk + 6
    w = key_expansion(text_to_bytes(key), Nb, Nr, Nk)
    state = text_to_matrix(plaintext)

    print_round(0, 'input', matrix_to_text(state), verbose)
    add_round_key(state, w, 0, Nb)
    print_round(0, 'k_sch', get_round_key(w, 0, Nb), verbose)

    for round in range(1, Nr):
        print_round(round, 'start', matrix_to_text(state), verbose)

        sub_bytes(state)
        print_round(round, 's_box', matrix_to_text(state), verbose)

        shift_rows(state)
        print_round(round, 's_row', matrix_to_text(state), verbose)

        mix_columns(state)
        print_round(round, 'm_col', matrix_to_text(state), verbose)

        add_round_key(state, w, round, Nb)
        print_round(round, 'k_sch', get_round_key(w, round, Nb), verbose)
    
    #inject
    grp = ( bit ) >> 5
    sub = ( bit & 0x18 ) >> 3
    off = ( bit & 0x07) 
    fault(state,grp,sub,off)
 
    #last round
    print_round(Nr, 'start', matrix_to_text(state), verbose)
    
    sub_bytes(state)
    print_round(Nr, 's_box', matrix_to_text(state), verbose)
    
    shift_rows(state)
    print_round(Nr, 's_row', matrix_to_text(state), verbose)

    add_round_key(state, w, Nr, Nb)
    print_round(Nr, 'k_sch', get_round_key(w, Nr, Nb), verbose)

    #print_round(Nr, 'output', matrix_to_text(state), True)
    print(f'{(127-bit):02x}: {matrix_to_text(state)}')

    return matrix_to_text(state)


def decrypt(ciphertext, key, verbose=False):
    """
    Perform the AES inverse cipher routine on the given ciphertext using the
given key.
    Specify verbose mode to print out each step of the routine.
    """
    Nb = 4
    Nk = int((len(key) * 4) / 32)
    Nr = Nk + 6
    w = key_expansion(text_to_bytes(key), Nb, Nr, Nk)
    state = text_to_matrix(ciphertext)

    print_round(0, 'iinput', matrix_to_text(state), verbose)
    add_round_key(state, w, Nr, Nb)
    print_round(0, 'ik_sch', get_round_key(
        w, Nr, Nb), verbose)

    for round in range(Nr-1, 0, -1):
        round_num = Nr-round

        print_round(round_num, 'istart', matrix_to_text(state), verbose)

        inv_shift_rows(state)
        print_round(round_num, 'is_row', matrix_to_text(state), verbose)

        inv_sub_bytes(state)
        print_round(round_num, 'is_box', matrix_to_text(state), verbose)

        print_round(round_num, 'ik_sch', get_round_key(w, round, Nb), verbose)
        add_round_key(state, w, round, Nb)

        print_round(round_num, 'ik_add', matrix_to_text(state), verbose)
        inv_mix_columns(state)

    print_round(Nr, 'istart', matrix_to_text(state), verbose)

    inv_shift_rows(state)
    print_round(Nr, 'is_row', matrix_to_text(state), verbose)

    inv_sub_bytes(state)
    print_round(Nr, 'is_box', matrix_to_text(state), verbose)

    print_round(Nr, 'ik_sch', get_round_key(w, 0, Nb), verbose)
    add_round_key(state, w, 0, Nb)

    print_round(Nr, 'ioutput', matrix_to_text(state), True)

    return matrix_to_text(state)


def xtime(a):
    """ Multiply the given polynomial (finite field) by x. """
    b = a << 1

    # If x^8 is set, XOR with irreducible polynomial 1B to return within range
    # AND with 0xffff to remove extraneous bits to the left
    if a & (1 << 7):
        b = (b ^ 0x1b) & 0b11111111

    return b


def ff_add(a, b):
    """ Add two finite fields (a and b) and return the result. """
    return a ^ b


def ff_multiply(a, b):
    """ Multiply two finite fields (a and b) and return the result. """
    result = 0

    for i in range(8):
        if a == 0 or b == 0:
            break

        # If the rightmost bit of a is set, we can add b to the result
        if a & 1:
            result = ff_add(result, b)

        # Continuously move down the bits of a while updating b
        b = xtime(b)
        a >>= 1

    return result

def fault(state, grp, sub, off):
    #print(f'fault: {grp} - {sub} - {off}')
    state[grp][sub] = state[grp][sub] ^ (1 << (7 - off))

def sub_bytes(state, s_box=s_box):
    """
    Process the State using a nonlinear byte substitution table (S-box)
    that operates on each of the State bytes independently.
    """
    for i in range(4):
        for j in range(4):
            state[i][j] = s_box[state[i][j]]


def inv_sub_bytes(state):
    """
    Apply the inverse of the byte substitution transformation, in which the 
    inverse S-box is applied to each byte of the State.
    """
    sub_bytes(state, s_box=inv_s_box)


def sub_word(word):
    """
    Take a four-byte input word and substitute each byte in the word with
    its appropriate value from the S-Box
    """
    bytes = [(word >> i & 0xff) for i in (24, 16, 8, 0)]
    return create_word([(s_box[bytes[i]]) for i in range(4)])


def rot_word(word):
    """ Perform a cyclic permutation on the input four-byte word. """
    bytes = [(word >> i & 0xff) for i in (24, 16, 8, 0)]
    return (bytes[1] << 24) | (bytes[2] << 16) | (bytes[3] << 8) | bytes[0]


def shift_rows(state):
    """
    Cyclically shift the bytes in the last three rows of the state over
different
    byte offsets.
    """
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][1], state[1][2], state[1][3], state[1][0]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][3], state[3][0], state[3][1], state[3][2]


def inv_shift_rows(state):
    """
    Apply the inverse of ShiftRows by cyclically shifting the bytes in the last
three
    rows by different byte offsets.
    """
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][3], state[1][0], state[1][1], state[1][2]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][1], state[3][2], state[3][3], state[3][0]


def mix_columns(state, m=ax):
    """
    Transformation in the Cipher that takes all of the columns of the State and 
    mixes their data (independently of one another) to produce new columns.
    """
    for c in range(4):
        rows = [0, 0, 0, 0]

        # For each value in the column, XOR with the result of multiplying
        # the value from the a(x) matrix with the value from the state
        for i in range(4):
            rows[0] ^= ff_multiply(m[0][i], state[i][c])
            rows[1] ^= ff_multiply(m[1][i], state[i][c])
            rows[2] ^= ff_multiply(m[2][i], state[i][c])
            rows[3] ^= ff_multiply(m[3][i], state[i][c])

        # Update the state only after calculating new values
        for r in range(4):
            state[r][c] = rows[r]


def inv_mix_columns(state):
    """
    Apply the inverse of MixColumns by taking all of the columns of the State
    and mixing their data (independently of one another) to produce new columns.
    """
    mix_columns(state, m=inv_ax)


def key_expansion(key_bytes, Nb, Nr, Nk):
    """ Generate and return a key schedule via the key expansion routine. """
    # Create an array of size (Nb * (Nr + 1))
    w = [None] * (Nb * (Nr + 1))

    # Generate the initial Nk words
    for i in range(Nk):
        w[i] = create_word([key_bytes[4*i], key_bytes[4*i+1],
                            key_bytes[4*i+2], key_bytes[4*i+3]])

    # Follow the key expansion routine from Nk to (Nb * (Nr + 1))
    # Almost a word-for-word translation of the pseudocode in FIPS-197 pp. 20
    for i in range(Nk, Nb * (Nr + 1)):
        temp = w[i-1]
        if i % Nk == 0:
            temp = sub_word(rot_word(temp)) ^ r_con[i // Nk]
        elif Nk > 6 and i % Nk == 4:
            temp = sub_word(temp)
        w[i] = w[i-Nk] ^ temp

    return w


def get_round_key(w, round, Nb):
    """ Get the round key from the key schedule for the given round as a string.
"""
    return ''.join(['{:08x}'.format(w[round * Nb + c]) for c in range(4)])


def add_round_key(state, w, round, Nb):
    """ Add a round key to the state via an XOR operation with the words from
the key schedule. """
    for c in range(4):
        word = w[round * Nb + c]
        bytes = [(word >> i & 0xff) for i in (24, 16, 8, 0)]
        for r in range(4):
            state[r][c] ^= bytes[r]


def create_word(byte_arr):
    """
    Take an array of 4 bytes and generate a single value representing a word.
    e.g. create_word([0x00, 0x11, 0x22, 0x33])
      => 0x00112233
    """
    return (byte_arr[0] << 24) | (byte_arr[1] << 16) | (byte_arr[2] << 8) | byte_arr[3]


def text_to_bytes(text):
    """
    Convert a string representing bytes into an array of integers.
    e.g. text_to_bytes("00112233445566778899aabbccddeeff")
      => [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa,
0xbb, 0xcc, 0xdd, 0xee, 0xff]
    """
    return [int(text[i] + text[i+1], 16) for i in range(0, len(text), 2)]


def text_to_matrix(text):
    """
    Convert a string representing 16 bytes into a 4x4 matrix.
    e.g. text_to_matrix("00112233445566778899aabbccddeeff")
      => [[0x00, 0x44, 0x88, 0xcc], 
          [0x11, 0x55, 0x99, 0xdd], 
          [0x22, 0x66, 0xaa, 0xee], 
          [0x33, 0x77, 0xbb, 0xff]]
    """
    matrix = []
    for i in range(0, 8, 2):
        matrix.append([int(text[i] + text[i+1], 16), int(text[i+8] + text[i+9], 16),
                      int(text[i+16] + text[i+17], 16), int(text[i+24] + text[i+25], 16)])
    return matrix


def matrix_to_text(matrix):
    """
    Convert a 4x4 matrix into a string representing 16 bytes.
    e.g. matrix_to_text([[0x00, 0x44, 0x88, 0xcc], 
                         [0x11, 0x55, 0x99, 0xdd], 
                         [0x22, 0x66, 0xaa, 0xee], 
                         [0x33, 0x77, 0xbb, 0xff]])
      => "00112233445566778899aabbccddeeff"
    """
    return ''.join(['{:02x}{:02x}{:02x}{:02x}'.format(
        matrix[0][c], matrix[1][c], matrix[2][c], matrix[3][c]) for c in
range(4)])


def print_round(round, step, value, verbose):
    """
    Print the value for a round (only in verbose mode)
    e.g. print_round(0, "input", "00112233445566778899aabbccddeeff")
      => round[ 0].input     00112233445566778899aabbccddeeff
    """
    if verbose:
        print('{:<19} {:}'.format(
            'round[{:2}].{:}'.format(round, step), value))


def perform_aes_algorithm(plaintext, key):
    """
    Perform the AES algorithm upon the given inputs with verbose printing.
    Follow the output format found in Appendix C of FIPS-197.
    """
    #if len(key) == 32:
    #    print('C.1   AES-128 (Nk=4, Nr=10)\n')

    #print('{:<19} {:}'.format('PLAINTEXT:', plaintext))
    #print('{:<19} {:}\n'.format('KEY:', key))

    #print('CIPHER (ENCRYPT):')
    plain = plaintext
    ciphertext = encrypt(plaintext, key, verbose=False)
    
    for i in range(128):
        plaintext = plain
        encrypt_inject(plaintext, key, i)

    #print('\nINVERSE CIPHER (DECRYPT):')
    #decrypt(ciphertext, key, verbose=False)


if __name__ == "__main__":
    #perform_aes_algorithm("00112233445566778899aabbccddeeff",
    #                       "000102030405060708090a0b0c0d0e0f")
    #perform_aes_algorithm("8c69c1b85cac31f4a562294e6729618f",
    #                      "84BBAD5CCDC538FCC120BF41711D2C2A")
    #perform_aes_algorithm("6433337a6e75747a6433337a6e75747a",
    #                       "6368756e677573646565657a6e75747a")
    from binascii import hexlify
    perform_aes_algorithm(hexlify(b'UMDCTF{urah4ackr}').decode('utf-8'),
                            hexlify(b'dR4g0N-d3eZn_uTs').decode('utf-8'))
