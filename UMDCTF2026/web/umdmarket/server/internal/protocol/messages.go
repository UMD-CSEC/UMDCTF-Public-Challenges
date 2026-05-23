package protocol

// Datagram types (server → client).
const (
	DatagramQuote    byte = 0x01
	DatagramResolved byte = 0x02
)

// Bidi-stream request types (client → server).
const (
	ReqRegister     byte = 0x20
	ReqLogin        byte = 0x21
	ReqSubscribe    byte = 0x22
	ReqUnsubscribe  byte = 0x23
	ReqFetchTickers byte = 0x24
	ReqFetchHistory byte = 0x25
	ReqResend       byte = 0x26
	ReqTrade        byte = 0x30
	ReqPortfolio    byte = 0x40
	ReqBuyFlag      byte = 0x50
)

// Response status codes.
const (
	StatusOK                    byte = 0x00
	StatusErrInvalidRequest     byte = 0x01
	StatusErrNotAuthenticated   byte = 0x02
	StatusErrCooldown           byte = 0x03
	StatusErrStale              byte = 0x04
	StatusErrInsufficientFunds  byte = 0x05
	StatusErrInsufficientPos    byte = 0x06
	StatusErrInvalidQty         byte = 0x07
	StatusErrMarketWarmup       byte = 0x08
	StatusErrTickerNotFound     byte = 0x09
	StatusErrInvalidCredentials byte = 0x0A
	StatusErrUsernameTaken      byte = 0x0B
	StatusErrWeakPassword       byte = 0x0C
	StatusErrAlreadyLoggedIn    byte = 0x0D
	StatusErrInvalidQuote       byte = 0x0E
	StatusErrResendUnavailable  byte = 0x0F
	StatusErrTickerResolved     byte = 0x10
)

// QuoteHMACSize is the number of bytes of HMAC-SHA256 output carried in each
// signed quote (truncated from the full 32-byte digest).
const QuoteHMACSize = 8

// Trade sides.
const (
	SideBuyYes  byte = 0x00
	SideBuyNo   byte = 0x01
	SideSellYes byte = 0x02
	SideSellNo  byte = 0x03
)
