package protocol

import (
	"encoding/binary"
	"io"
)

// PutU16 appends a little-endian uint16.
func PutU16(buf []byte, v uint16) {
	binary.LittleEndian.PutUint16(buf, v)
}

// PutU32 appends a little-endian uint32.
func PutU32(buf []byte, v uint32) {
	binary.LittleEndian.PutUint32(buf, v)
}

// PutU64 appends a little-endian uint64.
func PutU64(buf []byte, v uint64) {
	binary.LittleEndian.PutUint64(buf, v)
}

// WriteOK writes a success status byte followed by payload to w.
func WriteOK(w io.Writer, payload []byte) error {
	buf := make([]byte, 1+len(payload))
	buf[0] = StatusOK
	copy(buf[1:], payload)
	_, err := w.Write(buf)
	return err
}

// WriteError writes an error status byte followed by a length-prefixed message.
func WriteError(w io.Writer, status byte, msg string) error {
	msgBytes := []byte(msg)
	buf := make([]byte, 1+2+len(msgBytes))
	buf[0] = status
	PutU16(buf[1:3], uint16(len(msgBytes)))
	copy(buf[3:], msgBytes)
	_, err := w.Write(buf)
	return err
}

// EncodeQuoteDatagram builds a signed QUOTE datagram:
// [0x01] [seq:2] [ticker_id:2] [yes_price:2] [hmac:QuoteHMACSize].
// mac must be exactly QuoteHMACSize bytes.
func EncodeQuoteDatagram(seq, tickerID, yesPrice uint16, mac []byte) []byte {
	buf := make([]byte, 7+QuoteHMACSize)
	buf[0] = DatagramQuote
	PutU16(buf[1:3], seq)
	PutU16(buf[3:5], tickerID)
	PutU16(buf[5:7], yesPrice)
	copy(buf[7:], mac)
	return buf
}

// EncodeResolvedDatagram builds a RESOLVED datagram:
// [0x02] [ticker_id:2] [outcome:1].
// outcome: 0 = YES (market hit MaxPrice), 1 = NO (market hit MinPrice).
// Fired once when a market resolves; clients should wipe any positions
// they hold in that ticker. Trading resumes on the next tick at the
// ticker's initial price.
func EncodeResolvedDatagram(tickerID uint16, outcome byte) []byte {
	buf := make([]byte, 4)
	buf[0] = DatagramResolved
	PutU16(buf[1:3], tickerID)
	buf[3] = outcome
	return buf
}
