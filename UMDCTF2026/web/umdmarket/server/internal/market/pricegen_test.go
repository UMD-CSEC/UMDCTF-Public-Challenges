package market

import "testing"

// Tests for the Tick loop's resolution + reset behavior. The random walk
// itself isn't deterministic (it uses crypto/rand), so these tests force
// resolution by seeding extreme prices before calling Tick.

func TestTickResolvesAtMinPrice(t *testing.T) {
	m := NewMarket()
	// Seed every ticker at MinPrice+1 so a single tick can reach the lower
	// boundary.
	for i := range m.Prices {
		m.Prices[i] = MinPrice + 1
	}

	// Run a bunch of ticks; at least one ticker should resolve NO.
	sawNo := false
	for i := 0; i < 200 && !sawNo; i++ {
		for _, r := range m.Tick() {
			if r.Outcome == OutcomeNO {
				sawNo = true
				// After resolution the price must be the ticker's
				// InitialPrice, not MinPrice.
				if m.Prices[r.TickerID] != Tickers[r.TickerID].InitialPrice {
					t.Errorf("resolved ticker %d price=%d, want InitialPrice=%d",
						r.TickerID, m.Prices[r.TickerID], Tickers[r.TickerID].InitialPrice)
				}
			}
		}
	}
	if !sawNo {
		t.Fatalf("expected at least one NO resolution from price=%d in 200 ticks", MinPrice+1)
	}
}

func TestTickResolvesAtMaxPrice(t *testing.T) {
	m := NewMarket()
	for i := range m.Prices {
		m.Prices[i] = MaxPrice - 1
	}

	sawYes := false
	for i := 0; i < 200 && !sawYes; i++ {
		for _, r := range m.Tick() {
			if r.Outcome == OutcomeYES {
				sawYes = true
				if m.Prices[r.TickerID] != Tickers[r.TickerID].InitialPrice {
					t.Errorf("resolved ticker %d price=%d, want InitialPrice=%d",
						r.TickerID, m.Prices[r.TickerID], Tickers[r.TickerID].InitialPrice)
				}
			}
		}
	}
	if !sawYes {
		t.Fatalf("expected at least one YES resolution from price=%d in 200 ticks", MaxPrice-1)
	}
}

func TestResolutionResetsImmediately(t *testing.T) {
	// After a resolution fires, Snapshot must immediately show the
	// InitialPrice for that ticker on the same tick (not the boundary
	// price it hit momentarily).
	m := NewMarket()
	m.Prices[0] = MinPrice + 1
	// Force a resolution. Since the step is random we may need a few ticks,
	// but we assert that *on the tick that resolves*, the snapshot already
	// reflects the reset.
	for i := 0; i < 200; i++ {
		events := m.Tick()
		for _, r := range events {
			if r.TickerID == 0 {
				snap := m.Snapshot()
				if snap[0] != Tickers[0].InitialPrice {
					t.Errorf("post-resolution snapshot[0]=%d, want InitialPrice=%d",
						snap[0], Tickers[0].InitialPrice)
				}
				return
			}
		}
	}
	t.Fatalf("ticker 0 never resolved within 200 ticks")
}

func TestNoResolutionInInterior(t *testing.T) {
	// A market sitting comfortably in the interior should not resolve on a
	// single tick (the walk can only move MaxStep per tick). Seed all
	// tickers at mid-range and verify no resolution fires.
	m := NewMarket()
	for i := range m.Prices {
		m.Prices[i] = 5000
	}
	for i := 0; i < 50; i++ {
		if events := m.Tick(); len(events) > 0 {
			t.Fatalf("unexpected resolution at mid-range: %+v (tick %d)", events, i)
		}
	}
}

func TestPriceReportsAfterResolution(t *testing.T) {
	// The Price() accessor must still return the (post-reset) price even
	// right after a resolution, since resolution is instantaneous.
	m := NewMarket()
	m.Prices[0] = MinPrice + 1
	for i := 0; i < 200; i++ {
		events := m.Tick()
		for _, r := range events {
			if r.TickerID == 0 {
				p, ok := m.Price(0)
				if !ok {
					t.Fatalf("Price(0) not ok after resolution")
				}
				if p != Tickers[0].InitialPrice {
					t.Errorf("Price(0)=%d after resolution, want InitialPrice=%d",
						p, Tickers[0].InitialPrice)
				}
				return
			}
		}
	}
	t.Fatalf("ticker 0 never resolved within 200 ticks")
}
