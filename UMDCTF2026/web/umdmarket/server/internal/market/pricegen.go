package market

import (
	"crypto/rand"
	"math/big"
	"sync"
)

const (
	MaxStep   = 10
	MinPrice  = 1
	MaxPrice  = 9999
	PriceUnit = 10000
)

// Outcome is the side a market settled on when it hit a price boundary.
type Outcome uint8

const (
	OutcomeYES Outcome = 0
	OutcomeNO  Outcome = 1
)

// Resolution is the event published by Tick when a market hits a price
// boundary. Hitting MaxPrice resolves YES; hitting MinPrice resolves NO.
// After the event fires, the market price is immediately reset to the
// ticker's InitialPrice and trading resumes on the next tick; any open
// positions in that ticker are considered settled by the server (winners
// go to zero; losers too, since this CTF variant doesn't pay out — the
// resolution just wipes the market clean).
type Resolution struct {
	TickerID uint16
	Outcome  Outcome
}

// Market holds current prices for all tickers.
type Market struct {
	mu     sync.RWMutex
	Prices []uint16
}

// NewMarket creates a market with prices initialized from ticker definitions.
func NewMarket() *Market {
	prices := make([]uint16, len(Tickers))
	for i, t := range Tickers {
		prices[i] = t.InitialPrice
	}
	return &Market{Prices: prices}
}

// Tick advances all prices by one random step. Any ticker whose new price
// would land at or beyond a boundary resolves (YES at MaxPrice, NO at
// MinPrice), its price snaps back to its InitialPrice, and the event is
// returned so the caller can notify subscribers and settle positions.
func (m *Market) Tick() []Resolution {
	m.mu.Lock()
	defer m.mu.Unlock()

	var events []Resolution

	for i := range m.Prices {
		price := int(m.Prices[i])
		step := cryptoRandIntn(2*MaxStep+1) - MaxStep
		newPrice := price + step

		if newPrice <= MinPrice {
			events = append(events, Resolution{
				TickerID: uint16(i),
				Outcome:  OutcomeNO,
			})
			m.Prices[i] = Tickers[i].InitialPrice
		} else if newPrice >= MaxPrice {
			events = append(events, Resolution{
				TickerID: uint16(i),
				Outcome:  OutcomeYES,
			})
			m.Prices[i] = Tickers[i].InitialPrice
		} else {
			m.Prices[i] = uint16(newPrice)
		}
	}

	return events
}

// Snapshot returns a copy of all current prices keyed by ticker ID.
func (m *Market) Snapshot() map[uint16]uint16 {
	m.mu.RLock()
	defer m.mu.RUnlock()

	snap := make(map[uint16]uint16, len(m.Prices))
	for i, p := range m.Prices {
		snap[uint16(i)] = p
	}
	return snap
}

// Price returns the current price for a ticker.
func (m *Market) Price(tickerID uint16) (uint16, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if int(tickerID) >= len(m.Prices) {
		return 0, false
	}
	return m.Prices[tickerID], true
}

// cryptoRandIntn returns a cryptographically secure random int in [0, n).
func cryptoRandIntn(n int) int {
	max := big.NewInt(int64(n))
	val, err := rand.Int(rand.Reader, max)
	if err != nil {
		panic("crypto/rand failed: " + err.Error())
	}
	return int(val.Int64())
}
