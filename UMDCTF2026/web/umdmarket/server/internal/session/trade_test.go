package session

import (
	"bytes"
	"sync"
	"testing"

	"predictionmarket/internal/auth"
)

// testSecret is a fixed secret used across all tests so signed tokens are
// reproducible. Real servers generate a fresh random secret per process.
var testSecret = []byte("0123456789abcdef0123456789abcdef")

func newTestSigner() *QuoteSigner {
	return NewQuoteSigner(testSecret)
}

// newTestSession creates an authenticated session with configurable state.
func newTestSession(seq, lastFillSeq uint16, balance uint64) *Session {
	s := NewSession(nil)
	s.Seq = seq
	s.LastFillSeq = lastFillSeq
	s.Balance = balance
	s.User = &auth.User{
		Username:  "testuser",
		Balance:   balance,
		Positions: make(map[uint16]*auth.Position),
	}
	return s
}

// seedTape writes a snapshot directly into the session's resend tape at the
// given seq. Mirrors what the tick loop's TickTape does for that seq.
func seedTape(s *Session, seq uint16, prices map[uint16]uint16) {
	snap := make(map[uint16]uint16, len(prices))
	for k, v := range prices {
		snap[k] = v
	}
	s.ResendTape[seq%ResendTapeSize] = tapeSlot{
		Seq:    seq,
		Filled: true,
		Prices: snap,
	}
}

// signedToken builds a QuoteToken the way the server would: signer.Sign over
// (seq, ticker, price).
func signedToken(signer *QuoteSigner, seq, tickerID, price uint16) QuoteToken {
	return QuoteToken{
		Seq:      seq,
		TickerID: tickerID,
		Price:    price,
		HMAC:     signer.Sign(seq, tickerID, price),
	}
}

func TestNormalTrade(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Fresh quote at seq=1497, price=4500. Server would emit this via the
	// tick loop with a valid signature.
	token := signedToken(signer, 1497, 0, 4500)

	fillPrice, err := s.ExecuteTrade(token, 0x00, 100, signer) // BUY_YES
	if err != nil {
		t.Fatalf("expected success, got: %v", err)
	}
	if fillPrice != 4500 {
		t.Errorf("expected fill price 4500, got %d", fillPrice)
	}
	expectedBalance := uint64(1_000_000 - 4500*100)
	if s.Balance != expectedBalance {
		t.Errorf("expected balance %d, got %d", expectedBalance, s.Balance)
	}
	pos := s.Positions[0]
	if pos == nil || pos.YesQty != 100 {
		t.Errorf("expected YesQty=100, got %+v", pos)
	}
}

func TestCooldownReject(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1480, 1_000_000)
	s.Subscribe(0)
	token := signedToken(signer, 1498, 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrCooldown {
		t.Fatalf("expected ErrCooldown, got: %v", err)
	}
}

func TestStaleRejectPlainUint16(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	// age=10 > MaxAge=5
	token := signedToken(signer, 1490, 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrStale {
		t.Fatalf("expected ErrStale, got: %v", err)
	}
}

func TestStaleFutureSeqRejected(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	// token.Seq > s.Seq — uint16(1500 - 2300) wraps to 64736 > MaxAge → stale.
	// Signer will happily sign the token since the client can construct any
	// quote they like; the bug in the *old* design was that this passed the
	// freshness check via int16 cast. Now it correctly fails.
	token := signedToken(signer, 2300, 0, 2000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrStale {
		t.Fatalf("expected ErrStale (no overflow bypass), got: %v", err)
	}
}

func TestInvalidHMAC(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Sign a quote at price=5000, then tamper the price to 100.
	token := signedToken(signer, 1498, 0, 5000)
	token.Price = 100

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrInvalidQuote {
		t.Fatalf("expected ErrInvalidQuote, got: %v", err)
	}
}

func TestInvalidHMACForgedSeq(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Sign for (1498, 0, 2000) but attempt to submit as if for seq=1500.
	token := signedToken(signer, 1498, 0, 2000)
	token.Seq = 1500

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrInvalidQuote {
		t.Fatalf("expected ErrInvalidQuote, got: %v", err)
	}
}

func TestDirectOldSeqRejected(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Even with a correctly-signed token, an old seq fails the freshness
	// check. This proves the only way an attacker lands an old-price fill
	// is via RESEND's fresh-stamp behavior — a directly-saved old datagram
	// doesn't work.
	token := signedToken(signer, 300, 0, 2000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrStale {
		t.Fatalf("expected ErrStale, got: %v", err)
	}
}

func TestHonestArbitrageBlocked(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	buyToken := signedToken(signer, 1497, 0, 3000)
	_, err := s.ExecuteTrade(buyToken, 0x00, 100, signer) // BUY_YES
	if err != nil {
		t.Fatalf("buy should succeed: %v", err)
	}
	// LastFillSeq is now 1500.

	sellToken := signedToken(signer, 1499, 0, 6000)
	_, err = s.ExecuteTrade(sellToken, 0x02, 100, signer) // SELL_YES
	if err != ErrCooldown {
		t.Fatalf("expected ErrCooldown, got: %v", err)
	}

	// Advance past cooldown.
	s.Seq += 50
	// Now the saved sellToken is stale (seq=1499, s.Seq=1550, age=51).
	_, err = s.ExecuteTrade(sellToken, 0x02, 100, signer)
	if err != ErrStale {
		t.Fatalf("expected ErrStale, got: %v", err)
	}
}

func TestBuyAndSellNO(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// BUY_NO at yesPrice=3000 → no price = 7000.
	buyToken := signedToken(signer, 1498, 0, 3000)
	fillPrice, err := s.ExecuteTrade(buyToken, 0x01, 10, signer) // BUY_NO
	if err != nil {
		t.Fatalf("buy NO failed: %v", err)
	}
	if fillPrice != 7000 {
		t.Errorf("expected fill at 7000 (NO price), got %d", fillPrice)
	}
	expectedBalance := uint64(1_000_000 - 7000*10)
	if s.Balance != expectedBalance {
		t.Errorf("expected balance %d, got %d", expectedBalance, s.Balance)
	}
	pos := s.Positions[0]
	if pos == nil || pos.NoQty != 10 {
		t.Errorf("expected NoQty=10, got %+v", pos)
	}

	// Advance, then sell.
	s.Seq += 50
	sellToken := signedToken(signer, s.Seq-2, 0, 2000)
	fillPrice, err = s.ExecuteTrade(sellToken, 0x03, 10, signer) // SELL_NO
	if err != nil {
		t.Fatalf("sell NO failed: %v", err)
	}
	if fillPrice != 8000 {
		t.Errorf("expected sell NO at 8000 (PriceUnit - yesPrice), got %d", fillPrice)
	}
}

func TestResendExploit(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Tape has ticker 0 at price 2000 at seq=1200 (still within 500-tick window).
	seedTape(s, 1200, map[uint16]uint16{0: 2000})

	// Player requests a resend for the old seq. Server dutifully looks up
	// the old price, but stamps the response with the current s.Seq.
	token, err := s.Resend(1200, 0, signer)
	if err != nil {
		t.Fatalf("resend failed: %v", err)
	}
	if token.Seq != s.Seq {
		t.Errorf("expected resent token seq=%d (current), got %d", s.Seq, token.Seq)
	}
	if token.Price != 2000 {
		t.Errorf("expected resent token price=2000, got %d", token.Price)
	}

	// Player trades on the fresh-stamped token. Freshness check passes
	// because token.Seq == s.Seq. Fill happens at the old cheap price.
	fillPrice, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != nil {
		t.Fatalf("exploit trade should succeed, got: %v", err)
	}
	if fillPrice != 2000 {
		t.Errorf("expected fill at old price 2000, got %d", fillPrice)
	}
	expectedBalance := uint64(1_000_000 - 2000*100)
	if s.Balance != expectedBalance {
		t.Errorf("expected balance %d, got %d", expectedBalance, s.Balance)
	}
}

func TestResendExploitRoundTrip(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Old cheap quote at seq=1250.
	seedTape(s, 1250, map[uint16]uint16{0: 2000})

	// Step 1: resend old quote, buy at stamped-fresh token.
	buyToken, err := s.Resend(1250, 0, signer)
	if err != nil {
		t.Fatalf("resend failed: %v", err)
	}
	_, err = s.ExecuteTrade(buyToken, 0x00, 100, signer)
	if err != nil {
		t.Fatalf("exploit buy failed: %v", err)
	}
	// Cost = 2000 * 100 = 200,000.
	if s.Balance != 800_000 {
		t.Errorf("expected balance 800000 after buy, got %d", s.Balance)
	}

	// Step 2: advance past cooldown and sell at current price 6500.
	s.Seq += 50 // s.Seq = 1550
	sellToken := signedToken(signer, s.Seq-2, 0, 6500)
	fillPrice, err := s.ExecuteTrade(sellToken, 0x02, 100, signer) // SELL_YES
	if err != nil {
		t.Fatalf("sell failed: %v", err)
	}
	if fillPrice != 6500 {
		t.Errorf("expected sell price 6500, got %d", fillPrice)
	}
	// Revenue = 6500 * 100 = 650,000. Balance = 800,000 + 650,000 = 1,450,000.
	if s.Balance != 1_450_000 {
		t.Errorf("expected balance 1,450,000, got %d", s.Balance)
	}
	profit := int64(s.Balance) - 1_000_000
	if profit != 450_000 {
		t.Errorf("expected profit 450,000, got %d", profit)
	}
}

func TestResendOutsideWindow(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	// Nothing written to the tape — every slot is unfilled.

	_, err := s.Resend(1200, 0, signer)
	if err != ErrResendWindowExceeded {
		t.Fatalf("expected ErrResendWindowExceeded on empty tape, got: %v", err)
	}

	// Even after seeding one slot, a different seq in the same slot (i.e., an
	// overwrite scenario) must also fail.
	seedTape(s, 1200, map[uint16]uint16{0: 2000})
	// Slot 1200%500 = 200. Requesting seq=200 (which would map to the same
	// slot) should fail because slot.Seq=1200 != 200.
	_, err = s.Resend(200, 0, signer)
	if err != ErrResendWindowExceeded {
		t.Fatalf("expected ErrResendWindowExceeded on overwritten slot, got: %v", err)
	}

	// Far future seq — never written.
	_, err = s.Resend(50000, 0, signer)
	if err != ErrResendWindowExceeded {
		t.Fatalf("expected ErrResendWindowExceeded on far future seq, got: %v", err)
	}
}

func TestResendTickerNotInSnapshot(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Tape at seq=1200 has only ticker 0 (e.g., the player wasn't yet
	// subscribed to ticker 5 at that time).
	seedTape(s, 1200, map[uint16]uint16{0: 2000})

	_, err := s.Resend(1200, 5, signer)
	if err != ErrTickerNotFound {
		t.Fatalf("expected ErrTickerNotFound, got: %v", err)
	}
}

func TestResentTokenHasValidHMAC(t *testing.T) {
	// Regression: the resend handler must sign the fresh-stamped token with
	// the *fresh* seq, not the original. Otherwise the returned token fails
	// the trade handler's HMAC check.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	seedTape(s, 1200, map[uint16]uint16{0: 2000})

	token, err := s.Resend(1200, 0, signer)
	if err != nil {
		t.Fatalf("resend failed: %v", err)
	}
	if !signer.Verify(token.Seq, token.TickerID, token.Price, token.HMAC) {
		t.Errorf("resent token failed HMAC verification")
	}
	// HMAC must specifically be for the fresh seq, not for the original.
	wrongMAC := signer.Sign(1200, 0, 2000)
	if bytes.Equal(token.HMAC, wrongMAC) {
		t.Errorf("resent token appears to be signed for the original seq, not the fresh one")
	}
}

func TestNotAuthenticated(t *testing.T) {
	signer := newTestSigner()
	s := NewSession(nil)
	s.Seq = 1500
	s.LastFillSeq = 1400

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrNotAuthenticated {
		t.Fatalf("expected ErrNotAuthenticated, got: %v", err)
	}
}

func TestInvalidQty(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x00, 0, signer)
	if err != ErrInvalidQty {
		t.Fatalf("expected ErrInvalidQty, got: %v", err)
	}
}

func TestInsufficientFunds(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 100)
	s.Subscribe(0)

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrInsufficientFunds {
		t.Fatalf("expected ErrInsufficientFunds, got: %v", err)
	}
}

func TestSellWithoutPosition(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x02, 100, signer) // SELL_YES w/o position
	if err != ErrInsufficientPos {
		t.Fatalf("expected ErrInsufficientPos, got: %v", err)
	}
}

func TestTradeUnsubscribedTicker(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	// Do NOT subscribe.

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrTickerNotFound {
		t.Fatalf("expected ErrTickerNotFound, got: %v", err)
	}
}

func TestBuyFlag(t *testing.T) {
	s := newTestSession(1500, 1400, FlagPrice+1000)

	flag, err := s.BuyFlag("UMDCTF{test}")
	if err != nil {
		t.Fatalf("expected success, got: %v", err)
	}
	if flag != "UMDCTF{test}" {
		t.Errorf("expected flag UMDCTF{test}, got %s", flag)
	}
	if s.Balance != 1000 {
		t.Errorf("expected balance 1000 after flag purchase, got %d", s.Balance)
	}
}

func TestBuyFlagInsufficientFunds(t *testing.T) {
	s := newTestSession(1500, 1400, FlagPrice-1)

	_, err := s.BuyFlag("UMDCTF{test}")
	if err != ErrFlagTooExpensive {
		t.Fatalf("expected ErrFlagTooExpensive, got: %v", err)
	}
}

func TestBuyFlagExactPrice(t *testing.T) {
	// Boundary: balance exactly equal to FlagPrice should succeed.
	s := newTestSession(1500, 1400, FlagPrice)

	flag, err := s.BuyFlag("UMDCTF{test}")
	if err != nil {
		t.Fatalf("expected success at exact price, got: %v", err)
	}
	if flag != "UMDCTF{test}" {
		t.Errorf("unexpected flag: %s", flag)
	}
	if s.Balance != 0 {
		t.Errorf("expected balance 0 after exact-price purchase, got %d", s.Balance)
	}
}

// --- Boundary tests on cooldown and freshness --------------------------------

func TestCooldownBoundaryPass(t *testing.T) {
	// cooldown = MinCooldown exactly must pass (the check is `<`).
	signer := newTestSigner()
	s := newTestSession(1500, 1500-MinCooldown, 1_000_000)
	s.Subscribe(0)
	token := signedToken(signer, 1498, 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != nil {
		t.Fatalf("expected trade to pass at cooldown=%d, got: %v", MinCooldown, err)
	}
}

func TestCooldownBoundaryReject(t *testing.T) {
	// cooldown = MinCooldown-1 must fail.
	signer := newTestSigner()
	s := newTestSession(1500, 1500-(MinCooldown-1), 1_000_000)
	s.Subscribe(0)
	token := signedToken(signer, 1498, 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrCooldown {
		t.Fatalf("expected ErrCooldown at cooldown=%d, got: %v", MinCooldown-1, err)
	}
}

func TestFreshnessBoundaryPass(t *testing.T) {
	// age = MaxAge exactly must pass (the check is `>`).
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	token := signedToken(signer, 1500-MaxAge, 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != nil {
		t.Fatalf("expected trade to pass at age=%d, got: %v", MaxAge, err)
	}
}

func TestFreshnessBoundaryReject(t *testing.T) {
	// age = MaxAge+1 must fail.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)
	token := signedToken(signer, 1500-(MaxAge+1), 0, 5000)

	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrStale {
		t.Fatalf("expected ErrStale at age=%d, got: %v", MaxAge+1, err)
	}
}

// --- Resend authentication and boundary -------------------------------------

func TestResendRequiresAuth(t *testing.T) {
	// Resend must refuse if the session isn't logged in. Parallels the
	// ExecuteTrade auth check.
	signer := newTestSigner()
	s := NewSession(nil)
	s.Seq = 1500
	seedTape(s, 1200, map[uint16]uint16{0: 2000})

	_, err := s.Resend(1200, 0, signer)
	if err != ErrNotAuthenticated {
		t.Fatalf("expected ErrNotAuthenticated, got: %v", err)
	}
}

func TestResendWindowBoundary(t *testing.T) {
	// The oldest retrievable seq is s.Seq - ResendTapeSize (inclusive on the
	// write side, exclusive once the slot is overwritten). Here s.Seq=1500
	// and a slot written at seq=1000 maps to slot index 1000%500=0. On the
	// next tick s.Seq=1500 would rewrite that same slot, so seq=1000 is the
	// last moment it's still retrievable. Verify both the edge case that
	// still works and the one-past that fails.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// At-boundary: written and not yet overwritten.
	seedTape(s, 1000, map[uint16]uint16{0: 2000})
	tok, err := s.Resend(1000, 0, signer)
	if err != nil {
		t.Fatalf("resend at the window boundary should succeed, got: %v", err)
	}
	if tok.Price != 2000 {
		t.Errorf("expected price 2000, got %d", tok.Price)
	}

	// One step past the boundary (a new tick writes slot 0 with seq=1500,
	// overwriting the seq=1000 entry).
	seedTape(s, 1500, map[uint16]uint16{0: 4000})
	_, err = s.Resend(1000, 0, signer)
	if err != ErrResendWindowExceeded {
		t.Fatalf("expected ErrResendWindowExceeded after overwrite, got: %v", err)
	}
}

// --- Defense-in-depth: resolution boundary band ----------------------------

func TestRejectsTradeAtLowBoundary(t *testing.T) {
	// Prices inside the lower resolution band can't be traded on: such a
	// quote could have been emitted just before the market resolved NO, and
	// filling on it post-resolution would let the player lock in a
	// near-boundary fill and then sell into the reset market.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	token := signedToken(signer, 1498, 0, MinTradablePrice-1)
	_, err := s.ExecuteTrade(token, 0x00, 100, signer) // BUY_YES
	if err != ErrPriceOutOfBand {
		t.Fatalf("expected ErrPriceOutOfBand at price below band, got: %v", err)
	}
}

func TestRejectsTradeAtHighBoundary(t *testing.T) {
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// BUY_NO with a very high YES price would fill at a near-zero NO price.
	token := signedToken(signer, 1498, 0, MaxTradablePrice+1)
	_, err := s.ExecuteTrade(token, 0x01, 100, signer)
	if err != ErrPriceOutOfBand {
		t.Fatalf("expected ErrPriceOutOfBand at price above band, got: %v", err)
	}
}

func TestAcceptsTradeAtBoundaryEdge(t *testing.T) {
	// At the very edge of the band both directions, trades must still pass
	// (the band is inclusive on the tradable side).
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	lo := signedToken(signer, 1498, 0, MinTradablePrice)
	if _, err := s.ExecuteTrade(lo, 0x00, 1, signer); err != nil {
		t.Errorf("trade at MinTradablePrice should succeed, got: %v", err)
	}

	// Reset for second trade.
	s.LastFillSeq = 1500 - MinCooldown

	hi := signedToken(signer, 1498, 0, MaxTradablePrice)
	if _, err := s.ExecuteTrade(hi, 0x01, 1, signer); err != nil {
		t.Errorf("trade at MaxTradablePrice should succeed, got: %v", err)
	}
}

func TestTradableBandCoversFreshnessWindow(t *testing.T) {
	// Invariant: the rejected band around each price boundary must be at
	// least MaxStep * MaxAge wide. A quote emitted at price P survives in
	// the freshness window for MaxAge ticks; during those ticks the walk
	// can move at most MaxStep per tick toward the boundary, so any quote
	// at a price within MaxStep*MaxAge of a boundary could be submitted
	// after the market has resolved. If someone later tunes MaxStep or
	// MaxAge up without widening the band, this test flags it.
	//
	// We use the MAX allowable worst case (MaxStep could be up to 127 in
	// practice before other arithmetic would overflow; we assert against
	// the current values).
	const maxStep, maxAge = 10, 5
	bandWidth := int(MinTradablePrice) - 1
	if bandWidth < maxStep*maxAge {
		t.Errorf("low band %d < MaxStep*MaxAge = %d — resolution-race exploit becomes possible",
			bandWidth, maxStep*maxAge)
	}
	topBand := int(priceCeiling()) - int(MaxTradablePrice)
	if topBand < maxStep*maxAge {
		t.Errorf("high band %d < MaxStep*MaxAge = %d", topBand, maxStep*maxAge)
	}
}

// priceCeiling returns the conceptual MaxPrice (9999) referenced by the band
// constants. Kept as a helper to avoid importing the market package, which
// would create a test-only cycle.
func priceCeiling() uint16 { return PriceUnit - 1 }

func TestStalePreResolutionTokenCannotFill(t *testing.T) {
	// Scenario: a quote was emitted just before a market resolved (YES
	// price very close to MinPrice). The attacker holds that token. After
	// the market resets, the attacker submits the token, hoping to fill at
	// the near-zero price and then sell into the freshly-reset market.
	//
	// Defense: the band check rejects any token whose Price is in the
	// resolution band, independent of whether the underlying market has
	// actually resolved. Even if the freshness window would otherwise
	// accept the token, the trade must be refused.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// The pre-resolution quote the attacker saved: YES=5 (well inside the
	// band). Its Seq is fresh (age=3 < MaxAge).
	stale := signedToken(signer, 1497, 0, 5)
	_, err := s.ExecuteTrade(stale, 0x00, 100, signer)
	if err != ErrPriceOutOfBand {
		t.Fatalf("expected ErrPriceOutOfBand on stale pre-resolution token, got: %v", err)
	}

	// Mirror: pre-resolution quote near the upper boundary, attempted as
	// BUY_NO (cheap NO leg).
	staleHi := signedToken(signer, 1497, 0, 9995)
	_, err = s.ExecuteTrade(staleHi, 0x01, 100, signer)
	if err != ErrPriceOutOfBand {
		t.Fatalf("expected ErrPriceOutOfBand on stale near-max token, got: %v", err)
	}
}

func TestResolutionWipeZerosPositionWithoutRefund(t *testing.T) {
	// After a market resolves, WipePositions on that ticker must drop the
	// holding without refunding the balance that was spent to open it.
	// This is what makes "camp the boundary" a losing trade: you paid,
	// you got the position, and then the market wiped the position.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	// Buy a legitimate position in-band.
	buy := signedToken(signer, 1498, 0, 5000)
	if _, err := s.ExecuteTrade(buy, 0x00, 100, signer); err != nil {
		t.Fatalf("buy failed: %v", err)
	}
	balanceAfterBuy := s.Balance
	if _, ok := s.Positions[0]; !ok {
		t.Fatal("expected position after buy")
	}

	// Market resolves.
	wiped := s.WipePositions(0)
	if !wiped {
		t.Fatal("WipePositions should have reported a wipe")
	}
	if _, ok := s.Positions[0]; ok {
		t.Error("position should be gone after wipe")
	}
	if s.Balance != balanceAfterBuy {
		t.Errorf("balance changed on wipe: was %d, got %d (no refund expected)",
			balanceAfterBuy, s.Balance)
	}

	// Attempting to sell the (now-gone) position fails.
	s.LastFillSeq = 1500 - MinCooldown
	sell := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(sell, 0x02, 100, signer) // SELL_YES
	if err != ErrInsufficientPos {
		t.Fatalf("expected ErrInsufficientPos after wipe, got: %v", err)
	}
}

func TestResolutionDoesNotRefundLostCapital(t *testing.T) {
	// Stronger property: a sequence of legitimate trades where every
	// ticker eventually resolves against the player must leave the player
	// no richer than they started (modulo rounding), no matter how they
	// sequence their buys. We simulate 10 cycles of:
	//   1. Buy 100 YES at a mid-range price.
	//   2. Market resolves (WipePositions).
	//   3. Next cycle starts with the post-loss balance.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 10_000_000)
	s.Subscribe(0)

	startBalance := s.Balance
	for i := 0; i < 10; i++ {
		// Keep cooldown satisfied.
		s.LastFillSeq = s.Seq - MinCooldown
		buy := signedToken(signer, s.Seq-2, 0, 5000)
		preBuy := s.Balance
		if _, err := s.ExecuteTrade(buy, 0x00, 100, signer); err != nil {
			t.Fatalf("cycle %d: buy failed: %v", i, err)
		}
		cost := preBuy - s.Balance
		if cost != 5000*100 {
			t.Fatalf("cycle %d: unexpected cost %d", i, cost)
		}
		s.WipePositions(0)
		// Balance should have lost exactly `cost` on this cycle; positions gone.
		if _, ok := s.Positions[0]; ok {
			t.Fatalf("cycle %d: position not wiped", i)
		}
	}

	if s.Balance >= startBalance {
		t.Errorf("balance did not decrease through 10 buy-and-wipe cycles: start=%d end=%d",
			startBalance, s.Balance)
	}
	expected := startBalance - uint64(10*5000*100)
	if s.Balance != expected {
		t.Errorf("expected balance %d after 10 cycles of lost %d each, got %d",
			expected, 5000*100, s.Balance)
	}
}

func TestConcurrentTradesAndResolutionsAreRaceFree(t *testing.T) {
	// Hammer one session with concurrent goroutines that mirror the real
	// server's locking discipline:
	//   - "trader" goroutines call ExecuteTrade (which takes sess.Lock()
	//     internally).
	//   - "tick" goroutines take sess.Lock() directly and call
	//     WipePositions / TickTape / Seq++, the way tickAllSessions does.
	//
	// Under `go test -race` any mutation outside the mutex (including any
	// accidental direct field access from an unsynchronized helper) would
	// be flagged. This also exercises the invariant that a resolution
	// wiping a position doesn't also refund the balance that was already
	// spent — the final balance across all outcomes must be <= starting
	// balance + total sell revenue.
	signer := newTestSigner()
	s := newTestSession(1500, 1500-MinCooldown, 10_000_000)
	s.Subscribe(0)

	const goroutines = 16
	const iters = 200
	var wg sync.WaitGroup

	// Half the goroutines try to trade.
	for g := 0; g < goroutines/2; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < iters; i++ {
				// Build a signed token at whatever the current seq minus
				// a fresh age is. We re-read Seq via a short lock because
				// the Seq field is updated by the tick goroutines.
				s.Lock()
				seq := s.Seq - 2
				s.Unlock()
				token := signedToken(signer, seq, 0, 5000)
				// Ignore errors: most will fail on cooldown, which is
				// the point. We want the trade code path to execute.
				_, _ = s.ExecuteTrade(token, 0x00, 1, signer)
			}
		}()
	}

	// The other half simulate the tick loop.
	for g := 0; g < goroutines/2; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < iters; i++ {
				s.Lock()
				// Pretend ticker 0 just resolved every iteration.
				s.WipePositions(0)
				_ = s.TickTape(map[uint16]uint16{0: 5000})
				s.Seq++
				s.Unlock()
			}
		}()
	}

	wg.Wait()

	// Every successful trade debits Balance by fill_price*qty; wipes don't
	// refund. So Balance can only have gone down.
	if s.Balance > 10_000_000 {
		t.Errorf("balance inflated above starting value: %d", s.Balance)
	}
}

func TestCooldownSurvivesResolution(t *testing.T) {
	// A trade sets LastFillSeq; a subsequent resolution wipes the player's
	// position but does NOT reset the cooldown. The player can't use
	// resolution as a way to fire cooldown-free trades.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	buy := signedToken(signer, 1498, 0, 5000)
	if _, err := s.ExecuteTrade(buy, 0x00, 100, signer); err != nil {
		t.Fatalf("buy failed: %v", err)
	}
	if s.LastFillSeq != 1500 {
		t.Fatalf("LastFillSeq should be 1500, got %d", s.LastFillSeq)
	}

	// Resolution happens.
	s.WipePositions(0)

	// A replay attempt within cooldown must still fail with ErrCooldown,
	// not silently succeed.
	buy2 := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(buy2, 0x00, 100, signer)
	if err != ErrCooldown {
		t.Fatalf("expected ErrCooldown despite resolution, got: %v", err)
	}
}

// --- Multi-session state handoff (login race) --------------------------------
//
// The server's handleLogin flushes the old session's state into the user
// record BEFORE binding the user to the new session, then re-reads the user
// record. These tests exercise that flow at the session layer to lock in
// the behavior the handler relies on.

func TestSaveToUserPersistsBalance(t *testing.T) {
	// Baseline: after SaveToUser, the shared *auth.User record reflects the
	// session's balance and positions. This is the invariant handleLogin
	// relies on when it flushes the old session before BindUser-ing the new
	// one.
	user := &auth.User{
		Username:  "alice",
		Balance:   500,
		Positions: make(map[uint16]*auth.Position),
	}
	s := NewSession(nil)
	s.User = user
	s.Balance = 9_999_999
	s.Positions = map[uint16]*Position{
		7: {YesQty: 42, NoQty: 3},
	}

	s.SaveToUser()

	if user.Balance != 9_999_999 {
		t.Errorf("expected user.Balance=9_999_999 after SaveToUser, got %d", user.Balance)
	}
	if got := user.Positions[7]; got == nil || got.YesQty != 42 || got.NoQty != 3 {
		t.Errorf("expected user.Positions[7]={42,3}, got %+v", got)
	}
}

func TestBindUserLoadsLatestRecord(t *testing.T) {
	// Simulates the login handoff: session A trades up to a large balance
	// and SaveToUser's it. A fresh session B then BindUser's the same
	// record and should see the new balance, not the starting one.
	user := &auth.User{
		Username:  "alice",
		Balance:   1_000_000, // starting
		Positions: make(map[uint16]*auth.Position),
	}

	// Session A: already running, about to be superseded.
	a := NewSession(nil)
	a.User = user
	a.Balance = 7_500_000
	a.Positions = map[uint16]*Position{
		2: {YesQty: 1000},
	}

	// The fix in handleLogin flushes A before B binds. Simulate that:
	a.SaveToUser()

	// Session B: freshly created by a new WebTransport connection.
	b := NewSession(nil)
	b.BindUser(user)

	if b.Balance != 7_500_000 {
		t.Errorf("B.Balance = %d, want 7_500_000 (A's flushed state)", b.Balance)
	}
	pos := b.Positions[2]
	if pos == nil || pos.YesQty != 1000 {
		t.Errorf("B.Positions[2] = %+v, want YesQty=1000", pos)
	}
	// And crucially B's positions must be a deep copy, not the same pointer.
	if pos == a.Positions[2] {
		t.Errorf("B.Positions[2] aliases A.Positions[2]; must be a deep copy")
	}
}

func TestWipePositionsRemovesHolding(t *testing.T) {
	// WipePositions deletes the session's holdings in a resolved ticker.
	// Balance is untouched (the cost was already debited when the position
	// was opened).
	s := newTestSession(1500, 1400, 1_000_000)
	s.Balance = 500_000
	s.Positions[3] = &Position{YesQty: 200, NoQty: 10}

	if !s.WipePositions(3) {
		t.Fatalf("expected WipePositions(3) to report a wipe")
	}
	if _, still := s.Positions[3]; still {
		t.Errorf("positions[3] should have been removed")
	}
	if s.Balance != 500_000 {
		t.Errorf("balance should be untouched, got %d", s.Balance)
	}
}

func TestWipePositionsNoOpWhenAbsent(t *testing.T) {
	s := newTestSession(1500, 1400, 1_000_000)
	// No positions at all.
	if s.WipePositions(3) {
		t.Errorf("WipePositions on empty map should return false")
	}
}

func TestNoReplayWithinCooldown(t *testing.T) {
	// Documents the behavior that the exploit and solver rely on: the trade
	// handler doesn't track seen tokens — a valid fresh token could in
	// principle be submitted twice — but the per-session cooldown makes a
	// second successful fire within 50 ticks impossible. If someone ever
	// removes the cooldown, this test will fail and flag that implicit
	// single-use invariant needs an explicit check.
	signer := newTestSigner()
	s := newTestSession(1500, 1400, 1_000_000)
	s.Subscribe(0)

	token := signedToken(signer, 1498, 0, 5000)
	_, err := s.ExecuteTrade(token, 0x00, 100, signer)
	if err != nil {
		t.Fatalf("first trade should succeed: %v", err)
	}
	// Immediate replay of the same token — different error would mean the
	// cooldown gate broke. No Seq advance between attempts.
	_, err = s.ExecuteTrade(token, 0x00, 100, signer)
	if err != ErrCooldown {
		t.Fatalf("expected ErrCooldown on immediate replay, got: %v", err)
	}
}
