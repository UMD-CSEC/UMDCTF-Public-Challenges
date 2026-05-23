package protocol

import (
	"encoding/binary"
	"fmt"
	"io"
)

// ReadFull reads exactly len(buf) bytes from r.
func ReadFull(r io.Reader, buf []byte) error {
	_, err := io.ReadFull(r, buf)
	return err
}

// ReadU8 reads a single byte.
func ReadU8(r io.Reader) (byte, error) {
	var buf [1]byte
	if err := ReadFull(r, buf[:]); err != nil {
		return 0, err
	}
	return buf[0], nil
}

// ReadU16 reads a little-endian uint16.
func ReadU16(r io.Reader) (uint16, error) {
	var buf [2]byte
	if err := ReadFull(r, buf[:]); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint16(buf[:]), nil
}

// ReadU32 reads a little-endian uint32.
func ReadU32(r io.Reader) (uint32, error) {
	var buf [4]byte
	if err := ReadFull(r, buf[:]); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint32(buf[:]), nil
}

// ReadU64 reads a little-endian uint64.
func ReadU64(r io.Reader) (uint64, error) {
	var buf [8]byte
	if err := ReadFull(r, buf[:]); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint64(buf[:]), nil
}

// ReadLenPrefixedString reads a 1-byte length prefix followed by that many bytes.
func ReadLenPrefixedString(r io.Reader) (string, error) {
	length, err := ReadU8(r)
	if err != nil {
		return "", err
	}
	if length == 0 {
		return "", fmt.Errorf("empty string")
	}
	buf := make([]byte, length)
	if err := ReadFull(r, buf); err != nil {
		return "", err
	}
	return string(buf), nil
}

// ReadBytes reads exactly n bytes from r.
func ReadBytes(r io.Reader, n int) ([]byte, error) {
	buf := make([]byte, n)
	if err := ReadFull(r, buf); err != nil {
		return nil, err
	}
	return buf, nil
}
