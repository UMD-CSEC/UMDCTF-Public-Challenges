package session

import "errors"

var (
	ErrNotAuthenticated     = errors.New("not authenticated")
	ErrInvalidQty           = errors.New("invalid quantity")
	ErrMarketWarmup         = errors.New("market warming up")
	ErrCooldown             = errors.New("cooldown active")
	ErrStale                = errors.New("quote stale")
	ErrTickerNotFound       = errors.New("ticker not found")
	ErrInsufficientFunds    = errors.New("insufficient funds")
	ErrInsufficientPos      = errors.New("insufficient position")
	ErrInvalidSide          = errors.New("invalid side")
	ErrFlagTooExpensive     = errors.New("insufficient funds for flag")
	ErrInvalidQuote         = errors.New("invalid quote signature")
	ErrResendWindowExceeded = errors.New("requested seq outside resend window")
	ErrPriceOutOfBand       = errors.New("quote price near resolution boundary")
)

// MinTradablePrice / MaxTradablePrice bracket the price range a trade can
// fill at. Prices within this band of the boundary (at or near MinPrice=1
// or MaxPrice=9999) are rejected because such a quote could have been
// emitted just before a market resolved; filling at it post-resolution
// would let the client lock in a near-boundary price and then sell into
// the freshly-reset market. The band size (market.MaxStep * MaxAge = 50)
// covers the worst-case drift a quote can survive across a freshness
// window.
const (
	MinTradablePrice uint16 = 51
	MaxTradablePrice uint16 = 9949
)

// QuoteToken is the signed quote echoed by the client on trade.
// The HMAC is computed over (Seq, TickerID, Price) by the server when the
// quote is first emitted (via datagram or RESEND response) and verified on
// every trade.
type QuoteToken struct {
	Seq      uint16
	TickerID uint16
	Price    uint16
	HMAC     []byte
}

// ExecuteTrade executes a trade against a client-supplied signed quote.
// The quote must carry a valid HMAC from the server's signer and must be
// fresh (within MaxAge ticks of s.Seq). Fill price is taken directly from
// the token.
func (s *Session) ExecuteTrade(token QuoteToken, side uint8, qty uint32, signer *QuoteSigner) (uint16, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.Authenticated() {
		return 0, ErrNotAuthenticated
	}
	if qty == 0 {
		return 0, ErrInvalidQty
	}

	cooldown := s.Seq - s.LastFillSeq
	if cooldown < MinCooldown {
		return 0, ErrCooldown
	}

	if !signer.Verify(token.Seq, token.TickerID, token.Price, token.HMAC) {
		return 0, ErrInvalidQuote
	}

	// Freshness: the quote must not be older than MaxAge ticks. Plain uint16
	// subtraction — if token.Seq is "ahead" of s.Seq this wraps to a large
	// value, which fails the check.
	age := s.Seq - token.Seq
	if age > MaxAge {
		return 0, ErrStale
	}

	// Refuse tokens whose price is inside the resolution band. A quote that
	// close to a boundary could have been emitted just before a market
	// resolved; the client submitting it post-resolution would otherwise
	// lock in a near-boundary price and then sell into the freshly-reset
	// market for a near-costless profit.
	if token.Price < MinTradablePrice || token.Price > MaxTradablePrice {
		return 0, ErrPriceOutOfBand
	}

	if !s.IsSubscribed(token.TickerID) {
		return 0, ErrTickerNotFound
	}

	// NO contracts are priced as complement of YES.
	price := token.Price
	if side == 0x01 || side == 0x03 { // BUY_NO or SELL_NO
		price = PriceUnit - token.Price
	}

	cost := uint64(price) * uint64(qty)

	if side == 0x00 || side == 0x01 { // BUY_YES or BUY_NO
		if s.Balance < cost {
			return 0, ErrInsufficientFunds
		}
		s.Balance -= cost
		s.addPosition(token.TickerID, side, qty)
	} else if side == 0x02 || side == 0x03 { // SELL_YES or SELL_NO
		if !s.hasPosition(token.TickerID, side, qty) {
			return 0, ErrInsufficientPos
		}
		s.Balance += cost
		s.removePosition(token.TickerID, side, qty)
	} else {
		return 0, ErrInvalidSide
	}

	s.LastFillSeq = s.Seq
	return price, nil
}

// Resend retransmits a previously-emitted quote for the given (seq, tickerID).
// Intended use: the client detected a gap in its datagram stream and wants
// to catch up on a missed quote. The returned token is stamped with the
// current s.Seq and freshly signed so the client can immediately trade on it
// without hitting the staleness check.
func (s *Session) Resend(reqSeq, tickerID uint16, signer *QuoteSigner) (QuoteToken, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.Authenticated() {
		return QuoteToken{}, ErrNotAuthenticated
	}

	slot := s.ResendTape[reqSeq%ResendTapeSize]
	if !slot.Filled || slot.Seq != reqSeq {
		// Either the seq is in the future / never written, or the slot was
		// overwritten by a newer tick (requested seq is further back than
		// ResendTapeSize).
		return QuoteToken{}, ErrResendWindowExceeded
	}
	price, ok := slot.Prices[tickerID]
	if !ok {
		return QuoteToken{}, ErrTickerNotFound
	}

	// Stamp with current seq so the client can trade on the returned token
	// immediately. The price comes from the requested (possibly old) seq.
	freshSeq := s.Seq
	mac := signer.Sign(freshSeq, tickerID, price)
	return QuoteToken{
		Seq:      freshSeq,
		TickerID: tickerID,
		Price:    price,
		HMAC:     mac,
	}, nil
}

// BuyFlag attempts to purchase the flag for FlagPrice.
func (s *Session) BuyFlag(flag string) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.Authenticated() {
		return "", ErrNotAuthenticated
	}
	if s.Balance < FlagPrice {
		return "", ErrFlagTooExpensive
	}
	s.Balance -= FlagPrice
	return flag, nil
}
