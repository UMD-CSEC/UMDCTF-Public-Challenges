package session

import (
	"sync"

	"predictionmarket/internal/auth"
)

const (
	PriceUnit       = 10000
	MaxAge          = 5
	MinCooldown     = 50
	FlagPrice       = 10_000_000
	StartingBalance = 1_000_000

	// ResendTapeSize is the number of past ticks retained per session for
	// RESEND lookups. Slots older than this are overwritten.
	ResendTapeSize = 500
)

// Position tracks YES/NO contract quantities for a ticker.
type Position struct {
	YesQty uint32
	NoQty  uint32
}

// tapeSlot is one entry of the resend tape: the seq it was written for
// (so a lookup can detect overwrites on wrap) and the subscribed-ticker
// prices at that tick.
type tapeSlot struct {
	Seq    uint16
	Filled bool
	Prices map[uint16]uint16
}

// Session holds all per-connection state.
type Session struct {
	mu            sync.Mutex
	Seq           uint16
	LastFillSeq   uint16
	ResendTape    [ResendTapeSize]tapeSlot
	Subscriptions map[uint16]bool
	Balance       uint64
	Positions     map[uint16]*Position
	User          *auth.User
}

// NewSession creates a session with default state. The resend tape starts
// empty; it fills in as the tick loop calls TickTape. `initialPrices` is
// currently unused but the signature is preserved for call-site stability.
func NewSession(initialPrices map[uint16]uint16) *Session {
	_ = initialPrices
	return &Session{
		Seq:           0,
		Subscriptions: make(map[uint16]bool),
		Balance:       0,
		Positions:     make(map[uint16]*Position),
	}
}

// Lock acquires the session mutex.
func (s *Session) Lock() {
	s.mu.Lock()
}

// Unlock releases the session mutex.
func (s *Session) Unlock() {
	s.mu.Unlock()
}

// Authenticated returns whether a user is logged in.
func (s *Session) Authenticated() bool {
	return s.User != nil
}

// BindUser loads user state into the session.
func (s *Session) BindUser(user *auth.User) {
	s.User = user
	s.Balance = user.Balance
	s.Positions = make(map[uint16]*Position)
	for tid, pos := range user.Positions {
		s.Positions[tid] = &Position{
			YesQty: pos.YesQty,
			NoQty:  pos.NoQty,
		}
	}
}

// SaveToUser writes session state back to the user record.
func (s *Session) SaveToUser() {
	if s.User == nil {
		return
	}
	s.User.Balance = s.Balance
	s.User.Positions = make(map[uint16]*auth.Position)
	for tid, pos := range s.Positions {
		s.User.Positions[tid] = &auth.Position{
			YesQty: pos.YesQty,
			NoQty:  pos.NoQty,
		}
	}
}

// Subscribe starts tracking quotes for a ticker.
func (s *Session) Subscribe(tickerID uint16) {
	s.Subscriptions[tickerID] = true
}

// Unsubscribe stops tracking quotes for a ticker.
func (s *Session) Unsubscribe(tickerID uint16) {
	delete(s.Subscriptions, tickerID)
}

// IsSubscribed returns whether the session is subscribed to a ticker.
func (s *Session) IsSubscribed(tickerID uint16) bool {
	return s.Subscriptions[tickerID]
}

// WipePositions removes any holdings this session had in the given ticker.
// Called when a market resolves: the balance spent to buy the positions
// stays debited (no payout in this variant), and the position goes to 0.
// Returns true if a position existed and was removed.
func (s *Session) WipePositions(tickerID uint16) bool {
	if _, ok := s.Positions[tickerID]; ok {
		delete(s.Positions, tickerID)
		return true
	}
	return false
}

// TickTape records a snapshot of subscribed-ticker prices into the resend
// tape at the session's current Seq. Returns the snapshot so the caller can
// emit datagrams for each entry.
func (s *Session) TickTape(allPrices map[uint16]uint16) map[uint16]uint16 {
	snapshot := make(map[uint16]uint16, len(s.Subscriptions))
	for tid := range s.Subscriptions {
		if price, ok := allPrices[tid]; ok {
			snapshot[tid] = price
		}
	}
	s.ResendTape[s.Seq%ResendTapeSize] = tapeSlot{
		Seq:    s.Seq,
		Filled: true,
		Prices: snapshot,
	}
	return snapshot
}

func (s *Session) addPosition(tickerID uint16, side byte, qty uint32) {
	pos, ok := s.Positions[tickerID]
	if !ok {
		pos = &Position{}
		s.Positions[tickerID] = pos
	}
	if side == 0x00 { // BUY_YES
		pos.YesQty += qty
	} else if side == 0x01 { // BUY_NO
		pos.NoQty += qty
	}
}

func (s *Session) hasPosition(tickerID uint16, side byte, qty uint32) bool {
	pos, ok := s.Positions[tickerID]
	if !ok {
		return false
	}
	if side == 0x02 { // SELL_YES
		return pos.YesQty >= qty
	}
	if side == 0x03 { // SELL_NO
		return pos.NoQty >= qty
	}
	return false
}

func (s *Session) removePosition(tickerID uint16, side byte, qty uint32) {
	pos := s.Positions[tickerID]
	if side == 0x02 { // SELL_YES
		pos.YesQty -= qty
	} else if side == 0x03 { // SELL_NO
		pos.NoQty -= qty
	}
	if pos.YesQty == 0 && pos.NoQty == 0 {
		delete(s.Positions, tickerID)
	}
}
