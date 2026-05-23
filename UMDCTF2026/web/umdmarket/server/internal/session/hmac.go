package session

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/binary"

	"predictionmarket/internal/protocol"
)

// QuoteSigner signs and verifies quote tokens. Each signature covers
// (seq, ticker_id, yes_price) packed little-endian, MACed with HMAC-SHA256
// and truncated to protocol.QuoteHMACSize bytes.
type QuoteSigner struct {
	secret []byte
}

// NewQuoteSigner constructs a signer from a shared secret. The secret should
// be at least 32 bytes of cryptographically random material and is private to
// the server.
func NewQuoteSigner(secret []byte) *QuoteSigner {
	k := make([]byte, len(secret))
	copy(k, secret)
	return &QuoteSigner{secret: k}
}

func (s *QuoteSigner) compute(seq, tickerID, yesPrice uint16) []byte {
	var msg [6]byte
	binary.LittleEndian.PutUint16(msg[0:2], seq)
	binary.LittleEndian.PutUint16(msg[2:4], tickerID)
	binary.LittleEndian.PutUint16(msg[4:6], yesPrice)

	mac := hmac.New(sha256.New, s.secret)
	mac.Write(msg[:])
	sum := mac.Sum(nil)
	return sum[:protocol.QuoteHMACSize]
}

// Sign returns the MAC for the given quote fields.
func (s *QuoteSigner) Sign(seq, tickerID, yesPrice uint16) []byte {
	return s.compute(seq, tickerID, yesPrice)
}

// Verify checks the MAC against the given fields in constant time.
func (s *QuoteSigner) Verify(seq, tickerID, yesPrice uint16, mac []byte) bool {
	if len(mac) != protocol.QuoteHMACSize {
		return false
	}
	expected := s.compute(seq, tickerID, yesPrice)
	return hmac.Equal(expected, mac)
}
