from os import system, remove
from random import shuffle, randint, choice
from string import ascii_lowercase

PORT_MIN = 1
PORT_MAX = 65335

PORT = 42237

FLAG = "UMDCTF{dDSA-d_23+t0ta11y_n0t_NSFW_tCp_pAcKET-0_0-15039254&((*#@!}"

def compress_file(port, filename):
    system("7z a -tzip -p{} {}.zip {}".format(port, filename, filename))

def generate_ranges():
    range_1 = list(range(1, PORT))
    range_2 = list(range(PORT + 1, PORT_MAX + 1))

    shuffle(range_1)
    shuffle(range_2)

    range_1.append(PORT)
    range_2.append(PORT)

    with open("range_1.txt", "w+") as f:
        f.write(str(range_1));

    with open("range_2.txt", "w+") as f:
        f.write(str(range_2));

def read_ranges():
    range_1 = None;
    range_2 = None;

    with open("range_1.txt", "r") as f:
        range_1 = f.read();

    range_1 = range_1[1:]
    range_1 = range_1[:-1]
    range_1 = range_1.split(", ")

    with open("range_2.txt", "r") as f:
        range_2 = f.read();

    range_2 = range_2[1:]
    range_2 = range_2[:-1]
    range_2 = range_2.split(", ")

    return (range_1, range_2)

def generate_zip_file():
    for ranges in read_ranges():
        for i in range(0, len(ranges)):
            r = ranges[i]
            r_after = None if i >= len(ranges) - 1 else ranges[i + 1]
            
            random_msg = ''.join((choice(ascii_lowercase) for x in range(randint(4, 128))))

            payload = ("Go to port {} instead :(\n\nRandom message: {}").format(FLAG if r == PORT else r_after, random_msg)

            filename = "port-{}.txt".format(r)
            with open(filename, "w+") as f:
                f.write(payload)

            compress_file(r, filename)

            while True:
                try:
                    remove(filename)
                except OSError:
                    continue
                break
                
                
                    

#generate_ranges() #remove call once ranges are generated as .txt files; replace call to generate new ranges

generate_zip_file();



