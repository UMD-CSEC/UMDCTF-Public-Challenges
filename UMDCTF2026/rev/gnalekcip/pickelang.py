#!/usr/local/bin/python3.13
from io import BytesIO
import operator
import struct
from pickle import Unpickler


class Pickelang(Unpickler):
    def find_class(self, module, name):
        if name in ["add", "getitem"]:
            return getattr(operator, name)
        if name in ["pack", "unpack"]:
            return getattr(struct, name)
        if name == "input":
            return input
        raise NotImplementedError("no")

    def persistent_load(self, pid):
        pickelang = Pickelang(BytesIO(pid))
        pickelang.memo = self.memo
        return pickelang.load()

Pickelang(open('pickle.pkl','rb')).load()