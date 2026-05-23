package market

import (
	"sync"
	"time"
)

// HistoricalRecord is a point-in-time snapshot of all prices.
type HistoricalRecord struct {
	Timestamp time.Time
	Prices    map[uint16]uint16 // ticker_id -> yes_price
}

// History stores minute-by-minute historical price snapshots.
type History struct {
	mu      sync.RWMutex
	Records []HistoricalRecord
}

// NewHistory creates an empty history store.
func NewHistory() *History {
	return &History{}
}

// Record adds a snapshot to the history.
func (h *History) Record(prices map[uint16]uint16) {
	h.mu.Lock()
	defer h.mu.Unlock()

	// Deep copy the prices map.
	snap := make(map[uint16]uint16, len(prices))
	for k, v := range prices {
		snap[k] = v
	}

	h.Records = append(h.Records, HistoricalRecord{
		Timestamp: time.Now(),
		Prices:    snap,
	})
}

// Query returns the last `minutes` records for a specific ticker.
// Returns (timestamp_unix, yes_price) pairs.
func (h *History) Query(tickerID uint16, minutes int) []HistoricalRecord {
	h.mu.RLock()
	defer h.mu.RUnlock()

	total := len(h.Records)
	start := total - minutes
	if start < 0 {
		start = 0
	}

	result := make([]HistoricalRecord, 0, total-start)
	for _, r := range h.Records[start:] {
		if price, ok := r.Prices[tickerID]; ok {
			result = append(result, HistoricalRecord{
				Timestamp: r.Timestamp,
				Prices:    map[uint16]uint16{tickerID: price},
			})
		}
	}
	return result
}
