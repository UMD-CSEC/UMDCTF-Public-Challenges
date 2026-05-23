from io import BytesIO
import builtins
import random
import time
from pickle import *
import struct
import operator


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


class MemoRef:
    def __init__(self, index):
        self.index = index


class EmitPush:
    def __init__(self, value):
        self.value = value


class EmitPut:
    def __init__(self, index):
        self.index = index


def lit(value):
    return EmitPush(value)


def put(index):
    return EmitPut(index)


class Pickle:
    def __init__(self):
        self.payload = b""

    def raw(self, data):
        self.payload += data

    def build(self, stop=True) -> bytes:
        return self.payload + STOP if stop else self.payload

    def get(self, idx):
        if 0 <= idx < 256:
            self.raw(BINGET + struct.pack("<B", idx))
        elif 0 <= idx < 2**32:
            self.raw(LONG_BINGET + struct.pack("<I", idx))

    def put(self, idx):
        if 0 <= idx < 256:
            self.raw(BINPUT + struct.pack("<B", idx))
        elif 0 <= idx < 2**32:
            self.raw(LONG_BINPUT + struct.pack("<I", idx))

    def memoize(self):
        self.raw(MEMOIZE)

    def pop(self):
        self.raw(POP)

    def reduce(self):
        self.raw(REDUCE)

    def emit(self, *parts):
        for part in parts:
            match part:
                case MemoRef(index=index):
                    self.get(index)
                case EmitPush(value=value):
                    self.push(value)
                case EmitPut(index=index):
                    self.put(index)
                case bytes(data):
                    self.raw(data)
                case _:
                    raise TypeError(f"cannot emit: {part!r}")
        return self

    def __getitem__(self, index):
        return MemoRef(index)

    def __setitem__(self, index, val):
        if val is not None:
            self.push(val)
        self.put(index)
        self.pop()

    def push(self, obj, save_id=None):
        match obj:
            case MemoRef(index=index):
                self.get(index)
            case int(x):
                self.push_int(x)
            case str(x):
                self.push_str(x)
            case bytes(x):
                self.push_bytes(x)
            case tuple(x):
                self.push_tuple(x)
            case dict(x):
                self.push_dict(x)
            case None:
                self.raw(NONE)
            case list(x):
                self.push_list(x)
            case _:
                raise TypeError(f"cannot push: {obj}")

    def push_int(self, x):
        if x == 0:
            self.raw(NEWFALSE)
        elif x == 1:
            self.raw(NEWTRUE)
        elif 0 <= x < 256:
            self.raw(BININT1 + struct.pack("<B", x))
        elif 0 <= x <= 65535:
            self.raw(BININT2 + struct.pack("<H", x))
        elif -128 <= x < 0:
            self.raw(b"\x8a\x01" + struct.pack("<b", x))
        elif -2147483648 <= x <= 2147483647:
            self.raw(BININT + struct.pack("<i", x))
        else:
            self.raw(INT + b"%d\n" % x)

    def push_str(self, s):
        assert len(s) <= 255
        self.raw(SHORT_BINUNICODE + struct.pack("<B", len(s)) + s.encode())

    def push_bytes(self, s):
        if len(s) <= 255:
            self.raw(SHORT_BINBYTES + struct.pack("<B", len(s)) + s)
        else:
            self.raw(BINBYTES + struct.pack("<I", len(s)) + s)

    def push_tuple(self, obj):
        if not obj:
            self.raw(EMPTY_TUPLE)
        elif len(obj) == 1:
            self.push(obj[0])
            self.raw(TUPLE1)
        elif len(obj) == 2:
            self.push(obj[0])
            self.push(obj[1])
            self.raw(TUPLE2)
        elif len(obj) == 3:
            self.push(obj[0])
            self.push(obj[1])
            self.push(obj[2])
            self.raw(TUPLE3)
        else:
            self.raw(MARK)
            for o in obj:
                self.push(o)
            self.raw(TUPLE)

    def push_list(self, obj):
        if not obj:
            self.raw(EMPTY_LIST)
        else:
            self.raw(MARK)
            for o in obj:
                self.push(o)
            self.raw(LIST)

    def push_dict(self, obj):
        if not obj:
            self.raw(EMPTY_DICT)
            return
        self.raw(MARK)
        for k, v in obj.items():
            self.push(k)
            self.push(v)
        self.raw(DICT)

    def push_global(self, name):
        n = name.encode()
        self.raw(SHORT_BINSTRING + struct.pack("<B", len(n)) + n + DUP + STACK_GLOBAL)

    def call(self, index, *args):
        for x in args:
            self.push(x)
        for i in (ARG1, ARG2, ARG3, ARG4)[: len(args)][::-1]:
            self.put(i)
            self.pop()
        self.get(index)
        self.raw(BINPERSID)

    def callp(self, index, *args):
        self.get(index)
        self.push(args)
        self.raw(REDUCE)


# Shared top-level memo slots.
ARG1, ARG2, ARG3, ARG4 = 0, 1, 2, 3
GETITEM, ADD, PACK, INPUT = 4, 5, 6, 14
INP = 7
OP = 11
BITS, TMP, STATE = 13, 67, 69
SUCCESS, FAIL = 100, 101


def scramble_regs():
    global ARG1, ARG2, ARG3, ARG4, GETITEM, ADD, PACK, INPUT, INP, OP, BITS, TMP, STATE, SUCCESS, FAIL

    names = [
        "ARG1", "ARG2", "ARG3", "ARG4",
        "GETITEM", "ADD", "PACK", "INPUT",
        "INP", "OP", "BITS", "TMP",
        "STATE", "SUCCESS", "FAIL",
    ]

    g = globals()
    old = {k: g[k] for k in names}
    slots = [old[k] for k in names]
    new_slots = random.sample(range(256), k=len(names))

    new = dict(zip(names, new_slots))
    move = {old[k]: new[k] for k in names if old[k] != new[k]}

    p = Pickle()
    sp = __import__("struct").pack

    def get(i):
        p.raw((BINGET + bytes((i,))) if i < 256 else (LONG_BINGET + sp("<I", i)))

    def put(i):
        p.raw((BINPUT + bytes((i,))) if i < 256 else (LONG_BINPUT + sp("<I", i)))

    pending = dict(move)

    while pending:
        movable = [src for src, dst in pending.items() if dst not in pending]
        if movable:
            random.shuffle(movable)
            for src in movable:
                dst = pending.pop(src)
                get(src)
                put(dst)
                p.raw(POP)
            continue

        cur = random.choice(tuple(pending))
        seen = {}
        cyc = []
        while cur not in seen:
            seen[cur] = len(cyc)
            cyc.append(cur)
            cur = pending[cur]
        cyc = cyc[seen[cur]:]

        t = 256 + random.randrange(1, 1 << 15)

        get(cyc[-1])
        put(t)
        p.raw(POP)

        for i in range(len(cyc) - 1, 0, -1):
            get(cyc[i - 1])
            put(cyc[i])
            p.raw(POP)

        get(t)
        put(cyc[0])
        p.raw(POP)

        for src in cyc:
            pending.pop(src)

    for k, v in new.items():
        g[k] = v

    return p.build(False)
    


def die():
    p = Pickle()
    p.get(INPUT)
    p.get(FAIL)
    p.raw(TUPLE1)
    p.raw(REDUCE)
    p.push(b"hgQ")
    p.put(0x67)
    p.raw(BINPERSID)
    return p.build(False)


def win():
    p = Pickle()
    p.get(INPUT)
    p.get(SUCCESS)
    p.raw(TUPLE1)
    p.raw(REDUCE)
    return p.build(False)


def pickle_select():
    p = Pickle()
    p.get(GETITEM)
    p.push({255: p[ARG2], 0: p[ARG3]})
    p.get(GETITEM)
    p.get(PACK)
    p.push("i")
    p.get(ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(3)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()


def build_addmod():
    p = Pickle()
    p.get(GETITEM)
    p.raw(MARK)
    p.push(0)
    p.get(ADD)
    p.raw(DUP)
    p.get(ARG1)
    p.get(ARG2)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.get(ARG4)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ADD)
    p.push(255)
    p.get(ARG1)
    p.raw(DICT)
    p.get(GETITEM)
    p.get(PACK)
    p.push("i")
    p.get(ADD)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(3)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()

def build_add():
    p = Pickle()
    p.get(ADD)
    p.get(ARG1)
    p.get(ARG2)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()


def build_neg():
    p = Pickle()
    p.get(ARG1)
    p.put(ARG2)
    p.push(-1)
    p.put(ARG1)
    p.push(build_mul())
    p.raw(BINPERSID)
    return p.build()


def build_sub():
    p = Pickle()
    p.get(ADD)
    p.get(ARG1)
    p.push(-1)
    p.put(ARG1)
    p.pop()
    p.push(build_mul())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()

def build_square_or_apply():
    p = Pickle()
    p.get(ARG2)
    p.put(ARG1)
    p.get(OP)
    p.raw(BINPERSID)
    return p.build()

def build_addone():
    p = Pickle()
    p.get(ADD)
    p.get(ARG1)
    p.push(1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    for _ in range(3):
        p.raw(PROTO + b'\x05')
    return p.build(False)

def build_noop():
    p = Pickle()
    for _ in range(8):
        p.raw(PROTO + b'\x05')
    return p.build(False)


def build_reset():
    p = Pickle()
    p.push(0)
    p.put(ARG1)
    p.pop()
    for _ in range(6):
        p.raw(PROTO + b'\x05')
    return p.build(False)


def build_div():
    p = Pickle()
    p.get(ADD)
    p.raw(DUP)
    p.raw(DUP)

    p.raw(DUP)
    p.push(b'B')

    p.get(PACK)
    p.push('I')
    p.get(ADD)

    for _ in range(3):
        p.raw(DUP)
    p.get(ARG1)
    for _ in range(4):
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.get(ADD)
    for _ in range(16):
        p.raw(DUP)
    p.push(build_noop())
    p.put(ARG1)
    p.get(ADD)
    p.get(ARG2)
    p.push(-1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.pop()
    p.push(build_mul_bytes())
    p.raw(BINPERSID)
    p.push(build_addone())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    for _ in range(16):
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(b'.')
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(0)
    p.put(ARG1)
    p.pop()
    p.raw(BINPERSID)
    p.push(b'h%c.'%ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(BINPERSID)
    return p.build()

def build_mod():
    p = Pickle()
    p.get(ADD)
    p.raw(DUP)
    p.raw(DUP)

    p.raw(DUP)
    p.push(b'B')

    p.get(PACK)
    p.push('I')
    p.get(ADD)

    for _ in range(3):
        p.raw(DUP)
    p.get(ARG1)
    for _ in range(4):
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.get(ADD)
    for _ in range(16):
        p.raw(DUP)
    p.push(build_addone())
    p.put(ARG1)
    p.get(ADD)
    p.get(ARG2)
    p.push(-1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.pop()
    p.push(build_mul_bytes())
    p.raw(BINPERSID)
    p.push(build_reset())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    for _ in range(16):
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(b'.')
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(0)
    p.put(ARG1)
    p.pop()
    p.raw(BINPERSID)
    p.push(b'h%c.'%ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(BINPERSID)
    return p.build()


def build_step_and():
    p = Pickle()
    p.get(ADD)
    p.raw(DUP)
    p.get(ARG3)
    p.raw(DUP)
    p.raw(TUPLE2)
    p.raw(REDUCE) # ARG3 *= 2
    p.get(GETITEM)
    p.raw(MARK)
    for i, j in [(ARG1, 1), (ARG2, 0)]:
        p.get(GETITEM)
        p.raw(MARK)
        p.push("HH")
        p.get(PACK)
        p.push("I")
        p.get(ADD)
        p.get(i)
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(INST + b"a\nunpack\n")
        p.put(BITS)
        p.push(0)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(i)
        p.pop()
        p.get(GETITEM)
        p.get(BITS)
        p.push(1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        if j==1:
            p.put(TMP)
            p.push(rand_division(0))
            p.raw(BINPERSID)
        else:
            p.raw(DUP)
    p.raw(DICT)
    p.get(TMP)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG3)
    return p.build(False)


def get_apply():
    p = Pickle()
    p.get(ADD)
    p.raw(DUP * 4)
    p.push(build_step())
    for _ in range(4):
        p.raw(DUP + TUPLE2 + REDUCE)
    p.push(b".")
    p.raw(TUPLE2 + REDUCE + BINPERSID)
    return p.build()


def build_and():
    p = Pickle()
    p.push(0)
    p.put(ARG3)
    p.get(ADD)
    p.raw(DUP * 4)
    p.push(build_step_and())
    for _ in range(4):
        p.raw(DUP + TUPLE2 + REDUCE)
    p.push(b".")
    p.raw(TUPLE2 + REDUCE)
    p.raw(BINPERSID)
    return p.build()


def build_step_or():
    p = Pickle()
    p.get(ADD)
    p.raw(DUP)
    p.get(ARG3)
    p.raw(DUP)
    p.raw(TUPLE2)
    p.raw(REDUCE) # ARG3 *= 2
    p.get(GETITEM)
    p.raw(MARK)
    for i, j in [(ARG1, 1), (ARG2, 0)]:
        p.get(GETITEM)
        p.raw(MARK)
        p.push("HH")
        p.get(PACK)
        p.push("I")
        p.get(ADD)
        p.get(i)
        p.raw(DUP)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(INST + b"a\nunpack\n")
        p.put(BITS)
        p.push(0)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(i)
        p.pop()
        p.get(GETITEM)
        p.get(BITS)
        p.push(1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        if j==1:
            p.put(TMP)
            p.push(rand_division(1))
            p.raw(BINPERSID)
        else:
            p.raw(DUP)
    p.raw(DICT)
    p.get(TMP)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG3)
    return p.build(False)


def build_or():
    p = Pickle()
    p.push(0)
    p.put(ARG3)
    p.get(ADD)
    p.raw(DUP * 4)
    p.push(build_step_or())
    for _ in range(4):
        p.raw(DUP + TUPLE2 + REDUCE)
    p.push(b".")
    p.raw(TUPLE2 + REDUCE)
    p.raw(BINPERSID)
    return p.build()


def build_xor():
    p = Pickle()
    p.get(ADD)
    p.push(build_add())
    p.raw(BINPERSID)
    p.get(ADD)
    p.push(build_and())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.push(build_neg())
    p.raw(BINPERSID)
    p.raw(DUP)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()


def build_equals():
    p = Pickle()
    p.get(GETITEM)
    p.raw(MARK)
    p.get(ARG1)
    p.push(0)
    p.get(ARG2)
    p.push(1)
    p.raw(DICT)
    p.get(ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()


def build_equals_end():
    p = Pickle()
    p.get(GETITEM)
    p.raw(MARK)
    p.get(ARG1)
    p.push(b'h%c.'%ARG4)
    p.get(ARG2)
    p.push(b'h%c.'%STATE)
    p.raw(DICT)
    p.get(ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(BINPERSID)
    return p.build()


def build_mulmod():
    p = Pickle()
    p.get(ARG2)
    p.put(ARG3)
    p.push(0)
    p.put(ARG2)
    p.push(build_addmod())
    p.put(OP)
    p.push(get_apply())
    p.raw(BINPERSID)
    return p.build()


def build_bool():
    p = Pickle()
    p.get(GETITEM)
    p.get(PACK)
    p.raw(DUP)
    p.push(b'b')
    p.push(63)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.get(ARG1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push(0)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    return p.build()


def build_mul():
    p = Pickle()
    p.get(ARG2)
    p.put(ARG3)
    p.push(0)
    p.put(ARG2)
    p.push(build_add())
    p.put(OP)
    p.push(get_apply())
    p.raw(BINPERSID)
    return p.build()


def build_powmod():
    p = Pickle()
    p.get(ARG2)
    p.put(ARG3)
    p.push(1)
    p.put(ARG2)
    p.push(build_mulmod())
    p.put(OP)
    p.push(get_apply())
    p.raw(BINPERSID)
    return p.build()


def build_mul_bytes():
    p = Pickle()
    p.get(ARG2)
    p.put(ARG3)
    p.push(b"")
    p.put(ARG2)
    p.push(build_add())
    p.put(OP)
    p.push(get_apply())
    p.raw(BINPERSID)
    return p.build()


def build_step():
    p = Pickle()
    p.get(GETITEM)
    p.raw(MARK)
    p.push("HH")
    p.get(PACK)
    p.push("I")
    p.get(ADD)
    p.get(ARG3)
    p.raw(DUP)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(INST + b"a\nunpack\n")
    p.put(BITS)
    p.push(0)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG3)
    p.get(GETITEM)
    p.push(build_square_or_apply())
    p.raw(BINPERSID)
    p.put(ARG2)
    p.get(OP)
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.get(GETITEM)
    p.get(BITS)
    p.push(1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    return p.build(False)


def int2str():
    p = Pickle()
    p.push(())
    p.put(ARG4)
    p.push(10)
    p.put(ARG2)
    def b1():
        p = Pickle()
        p.get(ADD)
        p.push(build_mod())
        p.raw(BINPERSID)
        p.raw(TUPLE1)
        p.get(ARG4)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG4)
        p.pop()
        p.push(build_div())
        p.raw(BINPERSID)
        p.put(ARG1)
        p.push(decision())
        p.raw(BINPERSID)
        p.raw(BINPERSID)
        return p.build()
    def b2():
        p = Pickle()
        p.get(ARG4)
        return p.build()
    def decision():
        p = Pickle()
        p.push(0)
        p.put(ARG2)
        p.get(GETITEM)
        p.push({1:b2(), 0:p[TMP]})
        p.push(build_equals())
        p.raw(BINPERSID)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        return p.build()
    p.push(b1())
    p.put(TMP)
    p.raw(BINPERSID)
    return p.build()

def parse():
    p = Pickle()
    p.push(())
    p.put(ARG4)
    p.push(0)
    p.put(ARG3)
    def b1a():
        p = Pickle()
        p.get(ADD)
        p.get(ARG4)
        p.get(ARG1)
        p.raw(TUPLE1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG4)
        p.get(TMP)
        p.raw(BINPERSID)
        return p.build()
    def b1b():
        p = Pickle()
        p.get(GETITEM)
        p.push({chr(i):i for i in random.sample(range(128),k=128)})
        p.get(GETITEM)
        p.get(INP)
        p.get(ARG3)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG1)
        p.get(ADD)
        p.get(ARG3)
        p.push(1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG3)
        p.push(decision())
        p.raw(BINPERSID)
        return p.build()
    def b2():
        p = Pickle()
        p.get(ARG4)
        return p.build()
    def decision():
        p = Pickle()
        p.push(32)
        p.put(ARG2)
        p.get(GETITEM)
        p.push({1:b2(), 0:b1a()})
        p.push(build_equals())
        p.raw(BINPERSID)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(BINPERSID)
        return p.build()
    p.push(b1b())
    p.put(TMP)
    p.raw(BINPERSID)
    return p.build()


def check_tuple():
    p = Pickle()
    
    def decision():
        p = Pickle()
        p.get(GETITEM)
        p.push({1:die(), 0:b'\x89.'})
        p.push(build_equals())
        p.raw(BINPERSID)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(BINPERSID)

        p.push(build_add())
        p.put(OP)
        p.push(build_mul())
        p.raw(BINPERSID)
        p.put(ARG1)
        p.push(0)
        p.put(ARG2)
        p.get(GETITEM)
        p.push({1:die(), 0:b'\x89.'})
        p.push(build_equals())
        p.raw(BINPERSID)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(BINPERSID)
        return p.build()

    def endl(e, f):
        p = Pickle()
        p.push(e)
        p.put(ARG2)
        p.get(GETITEM)
        p.push({1:b'\x88.', 0:p[f]})
        p.push(build_equals())
        p.raw(BINPERSID)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.raw(BINPERSID)
        return p.build()
    
    def outer():
        p = Pickle()
        p.get(ADD)
        p.get(ARG3)
        p.push(1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG4)
        p.push(inner())
        p.raw(BINPERSID)
        p.pop()
        p.put(ARG3)
        p.put(ARG1)
        p.push(endl(8, TMP))
        p.raw(BINPERSID)
        return p.build()

    def inner():
        p = Pickle()
        p.get(GETITEM)
        p.get(OP)
        p.get(ARG3)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG1)
        p.get(GETITEM)
        p.get(OP)
        p.get(ARG4)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG2)
        p.push(decision())
        p.raw(BINPERSID)
        p.get(ADD)
        p.get(ARG4)
        p.push(1)
        p.raw(TUPLE2)
        p.raw(REDUCE)
        p.put(ARG4)
        p.put(ARG1)
        p.push(endl(9, BITS))
        p.raw(BINPERSID)
        return p.build()

    p.push(0)
    p.put(ARG3)
    p.get(ARG1)
    p.put(OP)
    p.push(inner())
    p.put(BITS)
    p.push(outer())
    p.put(TMP)
    p.raw(BINPERSID)
    return p.build()


def get_box(a):
    p = Pickle()
    p.raw(MARK)
    for i in a:
        p.get(GETITEM)
        p.get(STATE)
        p.push(i)
        p.raw(TUPLE2)
        p.raw(REDUCE)
    p.raw(TUPLE)
    return p.build(False)


def get_inp(idx, arg):
    p = Pickle()
    p.get(GETITEM)
    p.get(INP)
    p.push(idx)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(arg)
    p.emit(scramble_regs())
    p.pop()
    return p.build(False)


def rand_division(target):
    p = Pickle()

    b = 2**24
    while b.bit_length() >= 24:
        a = random.randrange(2**12, 2**16) # use 2**4 for testing.
        b = a*target + random.randrange(0, a)
    p.push(a)
    p.push(b)
    p.put(ARG1)
    p.pop()
    p.put(ARG2)
    p.push(build_div())
    p.raw(BINPERSID)
    return p.build()
    

def build_pickle():
    p = Pickle()

    scramble_regs()

    p.push_global("getitem")
    p.put(GETITEM)

    p.push_global("add")
    p.put(ADD)

    p.push_global("pack")
    p.put(PACK)

    p.push("Try again\n")
    p.put(BITS)

    p.push_global("input")
    p.put(INPUT)

    p.push("END")
    p.put(ARG4)

    p.push("Correct\n")
    p.put(SUCCESS)
    p.put(OP)
    p.put(ARG1)

    p.push("Incorrect\n")
    p.put(FAIL)
    p.put(ARG3)

    p.raw(MARK)
    p.push("flag? ")
    p.raw(b"ia\ninput\n")
    p.put(INP)

    p.push(67676769)
    p.put(TMP)

    p.push(())
    p.put(STATE)

    p.push(0xaa289)
    p.put(ARG1)

    p.push(10001)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(parse())
    p.raw(BINPERSID)
    p.put(INP)

    p.emit(scramble_regs())
    p.push(build_div()) # this is just a dos comment these two lines out if you don't want to build with it.
    p.raw(BINPERSID)
    p.put(ARG3)
    p.get(ADD)
    p.raw(DUP)
    p.get(STATE)
    p.push(3)
    p.raw(TUPLE1)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.put(STATE)
    p.push(22)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(0)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(build_xor())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.put(ARG1)
    p.push(4)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(build_mul())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.get(ADD)
    p.raw(DUP)
    p.get(STATE)

    p.emit(scramble_regs())
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push((4, 9))
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(STATE)

    p.emit(scramble_regs())
    p.get(ADD)
    p.get(GETITEM)
    p.get(INP)
    p.push(1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.push(5)
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG1)
    p.push(build_mul())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.push(11)

    p.emit(scramble_regs())
    p.put(ARG2)
    p.push(build_div())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.put(ARG1)
    p.push(3)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(build_sub())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.get(ADD)

    p.emit(scramble_regs())
    p.raw(DUP)
    p.raw(DUP)
    p.get(STATE)
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push(-1009)
    p.put(ARG4)
    p.push(169)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.pop()
    p.pop()
    p.get(GETITEM)
    p.get(INP)
    p.push(2)
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(build_powmod())
    p.raw(BINPERSID)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.get(GETITEM)
    p.get(INP)
    p.push(3)
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(STATE)

    p.emit(scramble_regs())
    p.push(rand_division(499))
    p.raw(BINPERSID)
    p.put(ARG1)
    p.get(GETITEM)

    p.emit(scramble_regs())
    p.get(INP)
    p.push(4)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.put(ARG2)
    p.push(build_addmod())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.get(ADD)

    p.emit(scramble_regs())
    p.raw(DUP*32)
    p.get(STATE)

    p.emit(scramble_regs())
    p.push(-10009)
    p.put(ARG4)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.get(ADD)
    p.push(275000)
    p.push(881)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.pop()
    p.get(GETITEM)
    p.get(INP)
    p.push(5)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.put(ARG2)
    p.pop()
    p.push(build_xor())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()

    p.emit(scramble_regs())
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.get(ADD)
    p.push(rand_division(1100))
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(6)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()

    p.emit(scramble_regs())
    p.push(3)
    p.put(ARG2)
    p.pop()
    p.push(build_mulmod())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.get(GETITEM)
    p.get(INP)

    p.emit(scramble_regs())
    p.push(7)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.push(rand_division(312))
    p.raw(BINPERSID)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.pop()
    p.pop()
    p.push_global('unpack')
    p.push(b'x3b')
    p.get(PACK)
    p.get(ADD)
    p.push(b'4b')

    p.emit(scramble_regs())
    p.raw(TUPLE1)
    p.push(build_powmod())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push((9, 8))
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push(690)
    p.put(ARG1)
    p.get(GETITEM)
    p.get(INP)
    p.push(8)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()

    p.emit(scramble_regs())
    p.pop()
    p.push(build_xor())
    p.raw(BINPERSID)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.raw(TUPLE1)
    p.pop()
    p.get(ADD)
    p.push(int2str())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.push((5,))
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push(80)
    p.put(ARG1)
    p.get(GETITEM)
    p.get(INP)
    p.push(9)

    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.pop()

    p.emit(scramble_regs())
    p.push(build_xor())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()

    p.emit(scramble_regs())
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push(28)
    p.put(ARG1)
    p.push(build_or())
    p.raw(BINPERSID)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(10)
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG2)
    p.push(build_and())
    p.raw(BINPERSID)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(build_mul())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.push(4227)
    p.put(ARG2)

    p.emit(scramble_regs())
    p.push(build_sub())
    p.raw(BINPERSID)
    p.put(ARG1)

    p.emit(scramble_regs())
    p.raw(POP * 7)
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.push((7,))
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(11)
    p.raw(TUPLE2)

    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG2)
    p.push(build_div())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.push(227)
    p.put(ARG2)
    p.push(build_xor())
    p.raw(BINPERSID)

    p.emit(scramble_regs())
    p.put(ARG1)
    p.raw(POP * 4)
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(12)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.emit(scramble_regs())
    p.push(945)
    p.put(ARG1)
    p.pop()
    p.push(build_sub())
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.push((1,5))
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.push(117)
    p.put(ARG2)
    p.get(GETITEM)
    p.get(INP)
    p.emit(scramble_regs())
    p.push(13)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.pop()
    p.push(build_xor())
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.emit(scramble_regs())
    p.push((9,6))
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.push(128)
    p.put(ARG1)
    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(INP)
    p.push(14)
    p.raw(TUPLE2)
    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.pop()
    p.push(build_or())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.push(211)
    p.put(ARG2)
    p.push(build_sub())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.emit(scramble_regs())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push((3,))
    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.get(GETITEM)
    p.get(INP)
    p.push(15)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.emit(scramble_regs())
    p.put(ARG2)
    p.put(ARG1)
    p.emit(scramble_regs())
    p.pop()
    p.push(build_mul())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.push(12580)
    p.emit(scramble_regs())
    p.put(ARG2)
    p.push(build_sub())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.push(512)
    p.emit(scramble_regs())
    p.put(ARG2)
    p.pop()
    p.get(GETITEM)
    p.get(INP)
    p.push(16)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(build_or())
    p.raw(BINPERSID)
    p.push(rand_division(350))
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.put(ARG1)
    p.pop()
    p.put(ARG2)
    p.push(build_addmod())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push((6,7,4))
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.get(ADD)
    p.push(64)
    p.emit(scramble_regs())
    p.put(ARG2)
    p.pop()
    p.get(GETITEM)
    p.get(INP)
    p.push(17)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.emit(scramble_regs())
    p.pop()
    p.push(build_xor())
    p.raw(BINPERSID)
    p.push(16)
    p.put(ARG1)
    p.pop()
    p.put(ARG2)
    p.pop()
    p.emit(scramble_regs())
    p.push(build_mulmod())
    p.raw(BINPERSID)
    p.push(1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push((1,))
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.get(GETITEM)
    p.get(INP)
    p.emit(scramble_regs())
    p.push(18)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.push(256)
    p.put(ARG2)
    p.pop()
    p.pop()
    p.push(build_or())
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.put(ARG1)
    p.push(83)
    p.put(ARG2)
    p.push(build_sub())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    p.get(GETITEM)
    p.get(INP)
    p.push(19)
    p.raw(TUPLE2)
    p.emit(scramble_regs())
    p.raw(REDUCE)
    p.put(ARG1)
    p.pop()
    p.push(52)
    p.put(ARG2)
    p.emit(scramble_regs())
    p.push(build_xor())
    p.raw(BINPERSID)
    p.put(ARG1)
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.push((7,2,8))
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.emit(scramble_regs())

    p.get(ADD)
    p.push(64)
    p.put(ARG1)
    p.pop()
    p.get(GETITEM)
    p.get(INP)
    p.emit(scramble_regs())
    p.push(20)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.pop()
    p.push(build_xor())
    p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.put(ARG1)
    p.push(18)
    p.put(ARG2)
    p.pop()
    p.emit(scramble_regs())
    p.pop()
    p.push(build_mul())
    p.raw(BINPERSID)
    p.push(13)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG1)
    p.emit(scramble_regs())
    p.pop()
    p.push(int2str())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.emit(scramble_regs())
    p.put(STATE)

    p.raw(MARK)
    
    # i ran out of sudoku squares so you can just have free bytes.
    p.raw(get_inp(21, ARG1))
    for i in range(22, 59):
        p.raw(get_inp(i, [ARG2, ARG1][i%2]))
        p.push(build_xor())
        p.raw(BINPERSID)

    p.raw(TUPLE)
    p.put(ARG2)
    
    # 3(268)49(571)(941)(67)(583)275(823)1(469)(462)98(731)5(51)9(362)7(84)(837)15(42)96(28)3(416)(957)674(593)1(281)(95)728(643)Z
    #   (85,   77,  68,  67,  84,    70,   123, 112,   105,  99,  107,  51, 108,   95,  111, 114,   95,    101, 108, 107,    99
    # 73, 80, 95, 119, 104, 49, 99, 72, 95, 48, 110, 101, 95, 49, 115, 95, 105, 55, 95, 53, 48, 52, 102, 52, 99, 52, 99, 53, 53, 53, 52, 52, 49, 52, 101, 53, 52, 125
    
    p.push((25, 15, 40, 31, 89, 82, 43, 23, 111, 94, 11, 58, 110, 66, 44, 54, 94, 104, 106, 5, 4, 82, 82, 87, 87, 87, 86, 0, 0, 1, 0, 5, 5, 81, 80, 1, 73))
    p.put(ARG1)
    p.push(build_equals_end())
    p.raw(BINPERSID)
    p.put(STATE)

    p.get(ADD)
    p.get(STATE)
    p.push(10)
    p.put(ARG1)
    p.emit(scramble_regs())
    p.raw(TUPLE1)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(STATE)
    p.get(PACK)
    p.push(b'I')
    p.emit(scramble_regs())
    p.get(GETITEM)
    p.get(STATE)
    p.push(81)
    p.raw(TUPLE2)
    p.raw(REDUCE)
    p.put(ARG2)
    p.emit(scramble_regs())
    p.pop()
    p.push(build_sub())
    p.raw(BINPERSID)
    p.raw(TUPLE2)
    p.raw(REDUCE)

    for box in random.sample([[*range(i*9, i*9+9)]for i in range(9)]+[[*range(i, 81, 9)]for i in range(9)]+[[i,i+1,i+2,i+9,i+10,i+11,i+18,i+19,i+20]for i in [0,3,6,27,30,33,54,57,60]],k=27):
      p.emit(get_box(box))
      p.emit(scramble_regs())
      p.put(ARG1)
      p.emit(scramble_regs())
      p.push(check_tuple())
      p.raw(BINPERSID)
    p.emit(scramble_regs())
    p.emit(scramble_regs())
    p.raw(win())
    p.emit(scramble_regs())
    p.emit(scramble_regs())
    p.push(None)
    return p.build()


def run_payload(payload: bytes, value: str) -> int:
    import builtins

    orig = builtins.input
    builtins.input = lambda a='': [print(a,end=''),value][1]
    try:
        return Pickelang(BytesIO(payload)).load()
    finally:
        builtins.input = orig


def main():
    payload = build_pickle()
    open('pickle.pkl','wb').write(payload)
    print(len(payload))
    got = run_payload(payload, "UMDCTF{pick3l_or_elkcIP_wh1cH_0ne_1s_i7_504f4c4c5554414e54} ")
    if type(got) == bytes:
        print(len(got), got[:10])
    else:
        print(got)

if __name__ == "__main__":
    main()
