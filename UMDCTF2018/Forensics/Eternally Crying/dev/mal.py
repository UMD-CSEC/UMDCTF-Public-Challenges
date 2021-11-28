"""This just makes me want to cry"""
import sys
import os

# Not in this directory
from malware import Malware

EXTENSION = ".barkbark"


class Ransomware(Malware):
    def __init__(self):
        super(Ransomware, self).__init__(sys.executable)
        self.counter = 0
        self.flag = "UMDCTF-{its-quite-noisy-here}"
        self._flag = self.flag.split()
        self._flag.reverse()
        self.encrypt_all(os.getcwd())

    def encrypt_all(self, path):
        for file in os.listdir(path):
            if os.path.isdir(file):
                try:
                    self.encrypt_all(file)
                except:
                    pass
            else:
                with open(file + EXTENSION, "w") as f:
                    f.write(" ")
                    f.close()
                self.counter += 1
                if self.counter % 100 == 0 and self._flag:
                    self.create_registry_key(key=self._flag.pop(), value=sys.executable)


if __name__ == "__main__":
    Ransomware()
