#!/usr/bin/env python3
"""Tiny .vmasm → .vmc assembler. Opcodes and widths must stay aligned with
src/vm.c. Directives: `.const "..."`, `.const_hex ...`, `.encrypt [magic_hi]`,
`label:`."""
import struct, sys, os, re, argparse

OPCODES = {
    'NOP': 0x8A, 'PUSH_I32': 0x37, 'PUSH_I64': 0x6B,
    'PUSH_CONST': 0x9F, 'PUSH_GLB': 0xA2,
    'POP': 0x15, 'DUP': 0x28, 'SWAP': 0x4D,
    'ADD': 0x52, 'SUB': 0x79, 'XOR': 0xB1, 'AND': 0xC6, 'OR': 0xD7,
    'EQ': 0x3C, 'NEQ': 0x89, 'LT': 0x5E, 'GT': 0x71,
    'JMP': 0x62, 'JZ': 0xAB, 'JNZ': 0xDC,
    'CONCAT': 0x93, 'SUBSTR': 0x47, 'LEN': 0x2A,
    'NATIVE': 0x58, 'INVOKE': 0xE4, 'RET': 0x1D, 'HALT': 0xFE,
    'SHL': 0x0B, 'SHR': 0x1F, 'MUL': 0x24, 'ROL': 0x34, 'ROR': 0x43,
    'LOAD_REG': 0x5A, 'STORE_REG': 0x66,
    'BSTR_LOAD_U32': 0x7E, 'U32_TO_BSTR': 0x8C,
}

# Instruction operand widths (in bytes after the opcode)
OP_WIDTH = {
    'NOP': 0, 'PUSH_I32': 4, 'PUSH_I64': 8, 'PUSH_CONST': 2, 'PUSH_GLB': 1,
    'POP': 0, 'DUP': 0, 'SWAP': 0,
    'ADD': 0, 'SUB': 0, 'XOR': 0, 'AND': 0, 'OR': 0,
    'EQ': 0, 'NEQ': 0, 'LT': 0, 'GT': 0,
    'JMP': 2, 'JZ': 2, 'JNZ': 2,
    'CONCAT': 0, 'SUBSTR': 0, 'LEN': 0,
    'NATIVE': 2, 'INVOKE': 2, 'RET': 0, 'HALT': 0,
    'SHL': 0, 'SHR': 0, 'MUL': 0, 'ROL': 0, 'ROR': 0,
    'LOAD_REG': 1, 'STORE_REG': 1,
    'BSTR_LOAD_U32': 0, 'U32_TO_BSTR': 0,
}

GLOBALS = { 'INNER_MSG': 0 }
NATIVES = { 'HASH_X': 2 }

def mwc_encrypt(buf: bytearray, magic_xor: int):
    s1 = (0x7FFF7FFF - magic_xor) & 0xFFFFFFFF
    s2 = magic_xor & 0xFFFFFFFF
    for i in range(len(buf)):
        s1 = (((s1 & 0xFFFF) * 36969) + (s1 >> 16)) & 0xFFFFFFFF
        s2 = ((s2 >> 16) + (s2 & 0xFFFF) * 18000) & 0xFFFFFFFF
        buf[i] ^= (s2 & 0xFF)

def parse_str_literal(tok):
    if tok.startswith('"'):
        # crude: handle \\xNN and \n
        s = tok[1:-1]
        out = bytearray()
        i = 0
        while i < len(s):
            c = s[i]
            if c == '\\' and i+1 < len(s):
                nxt = s[i+1]
                if nxt == 'n': out.append(0x0a); i += 2
                elif nxt == 't': out.append(0x09); i += 2
                elif nxt == '\\': out.append(0x5c); i += 2
                elif nxt == '"': out.append(0x22); i += 2
                elif nxt == 'x' and i+3 < len(s):
                    out.append(int(s[i+2:i+4], 16)); i += 4
                else:
                    out.append(ord(nxt)); i += 2
            else:
                out.append(ord(c)); i += 1
        return bytes(out)
    if tok.startswith('0x') or tok.startswith('0X'):
        return None
    return None

def parse_int(tok):
    tok = tok.rstrip(',')
    if tok.startswith('0x') or tok.startswith('-0x'):
        return int(tok, 16)
    return int(tok, 0)

def assemble(src, classes_idx=None):
    """classes_idx: dict mapping class name (no ext) -> index, for INVOKE."""
    if classes_idx is None:
        classes_idx = {}
    lines = src.splitlines()
    consts = []
    encrypt = False
    magic_hi = None
    out = bytearray()
    labels = {}
    fixups = []

    # Pre-pass: gather consts, pragmas
    body_lines = []
    for lineno, raw in enumerate(lines, 1):
        line = raw.split(';', 1)[0].split('#', 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        # .const_hex must be checked first — .const is a prefix of it.
        if stripped.startswith('.const_hex'):
            m = re.match(r'\.const_hex\s+([0-9a-fA-F]+)', stripped)
            if not m:
                raise SyntaxError(f'bad .const_hex at line {lineno}: {stripped}')
            consts.append(bytes.fromhex(m.group(1)))
            continue
        if stripped.startswith('.const'):
            m = re.match(r'\.const\s+"((?:[^"\\]|\\.)*)"', stripped)
            if not m:
                raise SyntaxError(f'bad .const at line {lineno}: {stripped}')
            s = m.group(1)
            consts.append(parse_str_literal('"'+s+'"'))
            continue
        if stripped.startswith('.encrypt'):
            encrypt = True
            toks = stripped.split()
            magic_hi = int(toks[1], 16) if len(toks) > 1 else 0xDAB1
            continue
        body_lines.append((lineno, stripped))

    # First code pass: compute addresses of labels
    pc = 0
    insns = []
    for lineno, line in body_lines:
        if line.endswith(':'):
            label = line[:-1].strip()
            labels[label] = pc
            continue
        parts = line.split(None, 1)
        op = parts[0].upper()
        if op not in OPCODES:
            raise SyntaxError(f'unknown op at line {lineno}: {op}')
        insns.append((lineno, op, parts[1] if len(parts) > 1 else ''))
        pc += 1 + OP_WIDTH[op]

    # Second code pass: emit bytes
    pc = 0
    for lineno, op, arg in insns:
        out.append(OPCODES[op])
        pc += 1
        width = OP_WIDTH[op]
        if op in ('PUSH_I32',):
            v = parse_int(arg.strip())
            out += struct.pack('<i', v)
        elif op == 'PUSH_I64':
            v = parse_int(arg.strip())
            out += struct.pack('<q', v)
        elif op == 'PUSH_CONST':
            v = parse_int(arg.strip())
            out += struct.pack('<H', v)
        elif op == 'PUSH_GLB':
            tok = arg.strip()
            v = GLOBALS[tok.upper()] if tok.upper() in GLOBALS else parse_int(tok)
            out.append(v & 0xff)
        elif op in ('JMP', 'JZ', 'JNZ'):
            label = arg.strip()
            fixups.append(('label', label, len(out), pc + 2, lineno))
            out += b'\x00\x00'
        elif op == 'NATIVE':
            toks = [t.strip() for t in arg.split(',')]
            h = NATIVES[toks[0].upper()] if toks[0].upper() in NATIVES else parse_int(toks[0])
            n = parse_int(toks[1])
            out.append(h & 0xff); out.append(n & 0xff)
        elif op == 'INVOKE':
            toks = [t.strip() for t in arg.split(',')]
            # first arg may be a class name
            first = toks[0]
            if first in classes_idx:
                c = classes_idx[first]
            else:
                c = parse_int(first)
            n = parse_int(toks[1])
            out.append(c & 0xff); out.append(n & 0xff)
        elif op in ('LOAD_REG', 'STORE_REG'):
            v = parse_int(arg.strip())
            out.append(v & 0xff)
        else:
            if width != 0:
                raise SyntaxError(f'unexpected width for {op}')
        pc += width

    # Resolve label fixups
    for kind, label, pos, ret_pc, lineno in fixups:
        if label not in labels:
            raise SyntaxError(f'unknown label {label} at line {lineno}')
        off = labels[label] - ret_pc
        struct.pack_into('<h', out, pos, off)

    # Build the class body as PLAINTEXT first:
    #   const_count (u16)  | code_len (u32)
    #   for each const: len (u16) | data (data_len bytes)
    #   code (code_len bytes)
    body_plain = bytearray()
    body_plain += struct.pack('<H', len(consts))
    body_plain += struct.pack('<I', len(out))
    for c in consts:
        body_plain += struct.pack('<H', len(c))
        body_plain += c
    body_plain += out

    # Build magic (4 bytes). Everything AFTER magic is either:
    #   - plaintext body as-is (CAFE classes)
    #   - fully MWC-encrypted body (BC3B classes) — including const_count,
    #     code_len, and per-const lengths, so structure-walking without
    #     decrypting is impossible.
    if encrypt:
        mhi = magic_hi & 0xFFFF
        header = bytes([0xBC, 0x3B, mhi & 0xFF, (mhi >> 8) & 0xFF])
        magic = int.from_bytes(header, 'little')
        magic_xor = magic ^ 0xBEBAFECA
        s1 = (0x7FFF7FFF - magic_xor) & 0xFFFFFFFF
        s2 = magic_xor & 0xFFFFFFFF
        body = bytearray(body_plain)
        for i in range(len(body)):
            s1 = (((s1 & 0xFFFF) * 36969) + (s1 >> 16)) & 0xFFFFFFFF
            s2 = ((s2 >> 16) + (s2 & 0xFFFF) * 18000) & 0xFFFFFFFF
            body[i] ^= (s2 & 0xFF)
    else:
        header = bytes([0xCA, 0xFE, 0x00, 0x00])
        body = body_plain

    return bytes(header + body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inputs', nargs='+')
    ap.add_argument('--out-dir', default='build/vm_out')
    ap.add_argument('--classes-idx', default='', help='comma-separated class name=idx list')
    args = ap.parse_args()

    classes_idx = {}
    if args.classes_idx:
        for kv in args.classes_idx.split(','):
            k, v = kv.split('=')
            classes_idx[k.strip()] = int(v)

    os.makedirs(args.out_dir, exist_ok=True)
    for src_path in args.inputs:
        with open(src_path) as f:
            src = f.read()
        obj = assemble(src, classes_idx=classes_idx)
        base = os.path.splitext(os.path.basename(src_path))[0]
        out_path = os.path.join(args.out_dir, base + '.vmc')
        with open(out_path, 'wb') as f:
            f.write(obj)
        print(f'{src_path} -> {out_path} ({len(obj)} bytes)')

if __name__ == '__main__':
    main()
