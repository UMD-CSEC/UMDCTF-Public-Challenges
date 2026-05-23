package server

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/quic-go/quic-go"
	"github.com/quic-go/quic-go/http3"
	"github.com/quic-go/webtransport-go"

	"predictionmarket/internal/auth"
	"predictionmarket/internal/market"
	"predictionmarket/internal/protocol"
	"predictionmarket/internal/session"
)


const (
	TickInterval    = 100 * time.Millisecond
	HistoryInterval = 600 // ticks between history snapshots (60s)
)

// Server is the prediction market WebTransport server.
type Server struct {
	market  *market.Market
	history *market.History
	users   *auth.UserStore
	flag    string
	signer  *session.QuoteSigner
	wt      *webtransport.Server
	done    chan struct{}

	sessionsMu sync.RWMutex
	sessions   map[string]*sessionEntry

	userSessionsMu sync.Mutex
	userSessions   map[string]string // username -> session ID
}

type sessionEntry struct {
	sess      *session.Session
	wtSession *webtransport.Session
	cancel    context.CancelFunc
}

// New creates a new Server.
func New(flag string) *Server {
	secret := make([]byte, 32)
	if _, err := rand.Read(secret); err != nil {
		// crypto/rand should never fail in practice; if it does, panic here
		// rather than running with a predictable signer.
		panic(fmt.Sprintf("generating quote signer secret: %v", err))
	}
	return &Server{
		market:       market.NewMarket(),
		history:      market.NewHistory(),
		users:        auth.NewUserStore(),
		flag:         flag,
		signer:       session.NewQuoteSigner(secret),
		done:         make(chan struct{}),
		sessions:     make(map[string]*sessionEntry),
		userSessions: make(map[string]string),
	}
}

// ListenAndServe starts the server on the given address using the certificate
// loaded from certPath/keyPath. Both files are expected to be PEM-encoded. The
// cert is baked at image build time (see cmd/certgen) so the frontend bundle
// can carry its SHA-256 hash for WebTransport's serverCertificateHashes.
func (srv *Server) ListenAndServe(addr, certPath, keyPath string) error {
	tlsCert, err := tls.LoadX509KeyPair(certPath, keyPath)
	if err != nil {
		return fmt.Errorf("loading TLS key pair from %s / %s: %w", certPath, keyPath, err)
	}
	// LoadX509KeyPair doesn't populate Leaf; parse the DER so we can log the
	// hashes.
	if tlsCert.Leaf == nil {
		if len(tlsCert.Certificate) == 0 {
			return fmt.Errorf("loaded certificate has no DER bytes")
		}
		leaf, err := x509.ParseCertificate(tlsCert.Certificate[0])
		if err != nil {
			return fmt.Errorf("parsing certificate: %w", err)
		}
		tlsCert.Leaf = leaf
	}

	certHash := sha256.Sum256(tlsCert.Leaf.Raw)
	log.Printf("Certificate SHA-256 hash: %s", hex.EncodeToString(certHash[:]))
	log.Printf("Certificate valid: %s to %s", tlsCert.Leaf.NotBefore.Format(time.RFC3339), tlsCert.Leaf.NotAfter.Format(time.RFC3339))
	spkiHash := sha256.Sum256(tlsCert.Leaf.RawSubjectPublicKeyInfo)
	log.Printf("SPKI hash (base64, for --ignore-certificate-errors-spki-list): %s", base64.StdEncoding.EncodeToString(spkiHash[:]))

	// Configure TLS with h3 ALPN.
	tlsConf := http3.ConfigureTLSConfig(&tls.Config{
		Certificates: []tls.Certificate{tlsCert},
	})

	mux := http.NewServeMux()
	mux.HandleFunc("/wt", func(w http.ResponseWriter, r *http.Request) {
		wtSess, err := srv.wt.Upgrade(w, r)
		if err != nil {
			log.Printf("WebTransport upgrade failed: %v", err)
			return
		}
		srv.handleSession(wtSess)
	})

	srv.wt = &webtransport.Server{
		H3: &http3.Server{
			Addr:      addr,
			TLSConfig: tlsConf,
			Handler:   mux,
			QUICConfig: &quic.Config{
				MaxIdleTimeout:  30 * time.Second,
				EnableDatagrams: true,
			},
		},
		CheckOrigin: func(r *http.Request) bool { return true },
	}

	// Configure the HTTP/3 server for WebTransport (enables settings, datagrams).
	webtransport.ConfigureHTTP3Server(srv.wt.H3)

	go srv.tickLoop()

	log.Printf("Listening on %s (HTTP/3 + WebTransport)", addr)
	return srv.wt.ListenAndServe()
}

// Close shuts down the server.
func (srv *Server) Close() error {
	close(srv.done)
	return srv.wt.Close()
}

// handleSession manages the lifecycle of a single WebTransport session.
func (srv *Server) handleSession(wtSess *webtransport.Session) {
	ctx, cancel := context.WithCancel(context.Background())
	sessionID := fmt.Sprintf("%p", wtSess)

	sess := session.NewSession(srv.market.Snapshot())
	entry := &sessionEntry{
		sess:      sess,
		wtSession: wtSess,
		cancel:    cancel,
	}

	srv.sessionsMu.Lock()
	srv.sessions[sessionID] = entry
	srv.sessionsMu.Unlock()

	defer func() {
		cancel()
		srv.removeSession(sessionID, sess)
		wtSess.CloseWithError(0, "")
	}()

	for {
		stream, err := wtSess.AcceptStream(ctx)
		if err != nil {
			return
		}
		go srv.handleStream(stream, sess, sessionID)
	}
}

func (srv *Server) removeSession(sessionID string, sess *session.Session) {
	sess.Lock()
	sess.SaveToUser()
	username := ""
	if sess.User != nil {
		username = sess.User.Username
	}
	sess.Unlock()

	srv.sessionsMu.Lock()
	delete(srv.sessions, sessionID)
	srv.sessionsMu.Unlock()

	if username != "" {
		srv.userSessionsMu.Lock()
		if srv.userSessions[username] == sessionID {
			delete(srv.userSessions, username)
		}
		srv.userSessionsMu.Unlock()
	}
}

// handleStream processes a single bidi stream (one request/response).
func (srv *Server) handleStream(stream *webtransport.Stream, sess *session.Session, sessionID string) {
	defer stream.Close()

	msgType, err := protocol.ReadU8(stream)
	if err != nil {
		return
	}

	switch msgType {
	case protocol.ReqRegister:
		srv.handleRegister(stream, sess)
	case protocol.ReqLogin:
		srv.handleLogin(stream, sess, sessionID)
	case protocol.ReqSubscribe:
		srv.handleSubscribe(stream, sess)
	case protocol.ReqUnsubscribe:
		srv.handleUnsubscribe(stream, sess)
	case protocol.ReqFetchTickers:
		srv.handleFetchTickers(stream)
	case protocol.ReqFetchHistory:
		srv.handleFetchHistory(stream)
	case protocol.ReqResend:
		srv.handleResend(stream, sess)
	case protocol.ReqTrade:
		srv.handleTrade(stream, sess)
	case protocol.ReqPortfolio:
		srv.handlePortfolio(stream, sess)
	case protocol.ReqBuyFlag:
		srv.handleBuyFlag(stream, sess)
	default:
		protocol.WriteError(stream, protocol.StatusErrInvalidRequest, "unknown message type")
	}
}

func (srv *Server) handleRegister(rw io.ReadWriter, sess *session.Session) {
	username, err := protocol.ReadLenPrefixedString(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad username")
		return
	}
	password, err := protocol.ReadLenPrefixedString(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad password")
		return
	}

	user, err := srv.users.Register(username, password)
	if err != nil {
		status := protocol.StatusErrInvalidRequest
		switch {
		case isWrapped(err, auth.ErrUsernameTaken):
			status = protocol.StatusErrUsernameTaken
		case isWrapped(err, auth.ErrWeakPassword):
			status = protocol.StatusErrWeakPassword
		case isWrapped(err, auth.ErrInvalidUsername):
			status = protocol.StatusErrInvalidRequest
		}
		protocol.WriteError(rw, status, err.Error())
		return
	}

	sess.Lock()
	sess.BindUser(user)
	sess.Unlock()

	payload := make([]byte, 8)
	binary.LittleEndian.PutUint64(payload, user.Balance)
	protocol.WriteOK(rw, payload)
}

func (srv *Server) handleLogin(rw io.ReadWriter, sess *session.Session, sessionID string) {
	username, err := protocol.ReadLenPrefixedString(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad username")
		return
	}
	password, err := protocol.ReadLenPrefixedString(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad password")
		return
	}

	user, err := srv.users.Login(username, password)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidCredentials, err.Error())
		return
	}

	// Disconnect existing session for this user. We have to be careful about
	// ordering here: the old session's defer will eventually run SaveToUser
	// to persist its state, and we want *that* to happen before we BindUser
	// on the new session — otherwise the new session reads a stale balance
	// from the user record and the old session's gains get clobbered on the
	// new session's eventual save.
	//
	// We do it synchronously here: take the old session's mutex, flush its
	// state into the user record ourselves, then release. After that the old
	// session's own deferred SaveToUser is a no-op (same data) and any
	// racing trade handlers on the old session are already blocked behind
	// its mutex.
	srv.userSessionsMu.Lock()
	if oldSessionID, exists := srv.userSessions[username]; exists && oldSessionID != sessionID {
		srv.sessionsMu.RLock()
		oldEntry, ok := srv.sessions[oldSessionID]
		srv.sessionsMu.RUnlock()
		if ok {
			// Cancel and close FIRST so no further streams can start trading
			// on the old session; then flush its state into the user record.
			// Ordering matters: if we flushed before cancel(), a stream that
			// AcceptStream was about to return could slip in between the
			// flush and the cancel, trade, and then the defer's SaveToUser
			// would overwrite what we just wrote.
			oldEntry.cancel()
			oldEntry.wtSession.CloseWithError(0x01, "logged in from another session")
			oldEntry.sess.Lock()
			oldEntry.sess.SaveToUser()
			oldEntry.sess.Unlock()
		}
	}
	srv.userSessions[username] = sessionID
	srv.userSessionsMu.Unlock()

	// Re-fetch the user record: if an old session just flushed above, the
	// Login() call earlier may have returned a stale snapshot.
	if fresh := srv.users.GetUser(username); fresh != nil {
		user = fresh
	}

	sess.Lock()
	sess.BindUser(user)
	sess.Unlock()

	payload := make([]byte, 8)
	binary.LittleEndian.PutUint64(payload[0:8], user.Balance)
	protocol.WriteOK(rw, payload)
}

func (srv *Server) handleSubscribe(rw io.ReadWriter, sess *session.Session) {
	tickerID, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad ticker_id")
		return
	}

	if int(tickerID) >= len(market.Tickers) {
		protocol.WriteError(rw, protocol.StatusErrTickerNotFound, "unknown ticker")
		return
	}

	sess.Lock()
	sess.Subscribe(tickerID)
	sess.Unlock()

	protocol.WriteOK(rw, nil)
}

func (srv *Server) handleUnsubscribe(rw io.ReadWriter, sess *session.Session) {
	tickerID, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad ticker_id")
		return
	}

	sess.Lock()
	sess.Unsubscribe(tickerID)
	sess.Unlock()

	protocol.WriteOK(rw, nil)
}

func (srv *Server) handleFetchTickers(w io.Writer) {
	tickers := market.Tickers

	size := 2
	for _, t := range tickers {
		size += 2 + 1 + len(t.Name) + 2 + len(t.Description)
	}

	payload := make([]byte, size)
	offset := 0
	binary.LittleEndian.PutUint16(payload[offset:], uint16(len(tickers)))
	offset += 2

	for _, t := range tickers {
		binary.LittleEndian.PutUint16(payload[offset:], t.ID)
		offset += 2
		payload[offset] = byte(len(t.Name))
		offset++
		copy(payload[offset:], t.Name)
		offset += len(t.Name)
		binary.LittleEndian.PutUint16(payload[offset:], uint16(len(t.Description)))
		offset += 2
		copy(payload[offset:], t.Description)
		offset += len(t.Description)
	}

	protocol.WriteOK(w, payload)
}

func (srv *Server) handleFetchHistory(rw io.ReadWriter) {
	tickerID, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad ticker_id")
		return
	}
	minutes, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad minutes")
		return
	}

	records := srv.history.Query(tickerID, int(minutes))

	payload := make([]byte, 2+len(records)*10)
	binary.LittleEndian.PutUint16(payload[0:2], uint16(len(records)))
	offset := 2
	for _, rec := range records {
		binary.LittleEndian.PutUint64(payload[offset:offset+8], uint64(rec.Timestamp.Unix()))
		offset += 8
		binary.LittleEndian.PutUint16(payload[offset:offset+2], rec.Prices[tickerID])
		offset += 2
	}

	protocol.WriteOK(rw, payload)
}

func (srv *Server) handleTrade(rw io.ReadWriter, sess *session.Session) {
	// Wire format: [seq:2] [ticker:2] [price:2] [hmac:QuoteHMACSize] [side:1] [qty:4]
	seq, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad seq")
		return
	}
	tickerID, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad ticker_id")
		return
	}
	price, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad price")
		return
	}
	mac, err := protocol.ReadBytes(rw, protocol.QuoteHMACSize)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad hmac")
		return
	}
	side, err := protocol.ReadU8(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad side")
		return
	}
	qty, err := protocol.ReadU32(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad qty")
		return
	}

	token := session.QuoteToken{
		Seq:      seq,
		TickerID: tickerID,
		Price:    price,
		HMAC:     mac,
	}

	fillPrice, err := sess.ExecuteTrade(token, side, qty, srv.signer)
	if err != nil {
		protocol.WriteError(rw, tradeErrToStatus(err), err.Error())
		return
	}

	payload := make([]byte, 10)
	binary.LittleEndian.PutUint16(payload[0:2], fillPrice)
	sess.Lock()
	binary.LittleEndian.PutUint64(payload[2:10], sess.Balance)
	sess.Unlock()
	protocol.WriteOK(rw, payload)
}

func (srv *Server) handleResend(rw io.ReadWriter, sess *session.Session) {
	// Wire format: [seq:2] [ticker:2]
	reqSeq, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad seq")
		return
	}
	tickerID, err := protocol.ReadU16(rw)
	if err != nil {
		protocol.WriteError(rw, protocol.StatusErrInvalidRequest, "bad ticker_id")
		return
	}

	token, err := sess.Resend(reqSeq, tickerID, srv.signer)
	if err != nil {
		protocol.WriteError(rw, resendErrToStatus(err), err.Error())
		return
	}

	payload := make([]byte, 6+protocol.QuoteHMACSize)
	binary.LittleEndian.PutUint16(payload[0:2], token.Seq)
	binary.LittleEndian.PutUint16(payload[2:4], token.TickerID)
	binary.LittleEndian.PutUint16(payload[4:6], token.Price)
	copy(payload[6:], token.HMAC)
	protocol.WriteOK(rw, payload)
}

func (srv *Server) handlePortfolio(w io.Writer, sess *session.Session) {
	sess.Lock()
	if !sess.Authenticated() {
		sess.Unlock()
		protocol.WriteError(w, protocol.StatusErrNotAuthenticated, "not authenticated")
		return
	}

	type posEntry struct {
		tid    uint16
		yesQty uint32
		noQty  uint32
	}
	positions := make([]posEntry, 0, len(sess.Positions))
	for tid, pos := range sess.Positions {
		positions = append(positions, posEntry{tid, pos.YesQty, pos.NoQty})
	}
	balance := sess.Balance
	sess.Unlock()

	payload := make([]byte, 10+len(positions)*10)
	binary.LittleEndian.PutUint64(payload[0:8], balance)
	binary.LittleEndian.PutUint16(payload[8:10], uint16(len(positions)))
	offset := 10
	for _, p := range positions {
		binary.LittleEndian.PutUint16(payload[offset:offset+2], p.tid)
		offset += 2
		binary.LittleEndian.PutUint32(payload[offset:offset+4], p.yesQty)
		offset += 4
		binary.LittleEndian.PutUint32(payload[offset:offset+4], p.noQty)
		offset += 4
	}

	protocol.WriteOK(w, payload)
}

func (srv *Server) handleBuyFlag(w io.Writer, sess *session.Session) {
	flagStr, err := sess.BuyFlag(srv.flag)
	if err != nil {
		status := protocol.StatusErrInsufficientFunds
		if err == session.ErrNotAuthenticated {
			status = protocol.StatusErrNotAuthenticated
		}
		protocol.WriteError(w, status, err.Error())
		return
	}

	flagBytes := []byte(flagStr)
	payload := make([]byte, 2+len(flagBytes))
	binary.LittleEndian.PutUint16(payload[0:2], uint16(len(flagBytes)))
	copy(payload[2:], flagBytes)
	protocol.WriteOK(w, payload)
}

func tradeErrToStatus(err error) byte {
	switch err {
	case session.ErrNotAuthenticated:
		return protocol.StatusErrNotAuthenticated
	case session.ErrCooldown:
		return protocol.StatusErrCooldown
	case session.ErrStale:
		return protocol.StatusErrStale
	case session.ErrInsufficientFunds:
		return protocol.StatusErrInsufficientFunds
	case session.ErrInsufficientPos:
		return protocol.StatusErrInsufficientPos
	case session.ErrInvalidQty:
		return protocol.StatusErrInvalidQty
	case session.ErrMarketWarmup:
		return protocol.StatusErrMarketWarmup
	case session.ErrTickerNotFound:
		return protocol.StatusErrTickerNotFound
	case session.ErrInvalidSide:
		return protocol.StatusErrInvalidRequest
	case session.ErrInvalidQuote:
		return protocol.StatusErrInvalidQuote
	case session.ErrPriceOutOfBand:
		return protocol.StatusErrTickerResolved
	default:
		return protocol.StatusErrInvalidRequest
	}
}

func resendErrToStatus(err error) byte {
	switch err {
	case session.ErrNotAuthenticated:
		return protocol.StatusErrNotAuthenticated
	case session.ErrResendWindowExceeded:
		return protocol.StatusErrResendUnavailable
	case session.ErrTickerNotFound:
		return protocol.StatusErrTickerNotFound
	default:
		return protocol.StatusErrInvalidRequest
	}
}

func isWrapped(err, target error) bool {
	for err != nil {
		if err == target {
			return true
		}
		unwrapped, ok := err.(interface{ Unwrap() error })
		if !ok {
			return false
		}
		err = unwrapped.Unwrap()
	}
	return false
}

// --- Tick Loop ---

func (srv *Server) tickLoop() {
	ticker := time.NewTicker(TickInterval)
	defer ticker.Stop()

	var tickCount uint64

	for {
		select {
		case <-ticker.C:
			resolutions := srv.market.Tick()
			allPrices := srv.market.Snapshot()
			srv.tickAllSessions(allPrices, resolutions)

			tickCount++
			if tickCount%HistoryInterval == 0 {
				srv.history.Record(allPrices)
			}

		case <-srv.done:
			return
		}
	}
}

func (srv *Server) tickAllSessions(allPrices map[uint16]uint16, resolutions []market.Resolution) {
	srv.sessionsMu.RLock()
	entries := make([]*sessionEntry, 0, len(srv.sessions))
	for _, entry := range srv.sessions {
		entries = append(entries, entry)
	}
	srv.sessionsMu.RUnlock()

	// Pre-build the RESOLVED datagrams once per tick so we send identical
	// bytes to every subscriber.
	resolvedDgrams := make([][]byte, 0, len(resolutions))
	for _, r := range resolutions {
		resolvedDgrams = append(resolvedDgrams, protocol.EncodeResolvedDatagram(r.TickerID, byte(r.Outcome)))
	}

	for _, entry := range entries {
		// Do all state mutation under the session lock; build the
		// datagrams we need to send, but don't actually call SendDatagram
		// here. SendDatagram blocks when the per-session send queue fills
		// up (quic-go bounds it at 32 frames) and holding sess.mu across
		// that block would stall every concurrent trade/resend on this
		// session.
		entry.sess.Lock()

		for _, r := range resolutions {
			entry.sess.WipePositions(r.TickerID)
		}

		snapshot := entry.sess.TickTape(allPrices)
		seq := entry.sess.Seq
		entry.sess.Seq++

		// Build signed QUOTE datagrams under the lock so the seq captured
		// above matches the one we sign.
		quoteDgrams := make([][]byte, 0, len(snapshot))
		for tid, price := range snapshot {
			mac := srv.signer.Sign(seq, tid, price)
			quoteDgrams = append(quoteDgrams, protocol.EncodeQuoteDatagram(seq, tid, price, mac))
		}

		entry.sess.Unlock()

		// Lock released: now we can block on SendDatagram without holding
		// anything. Broadcast resolution events first so the client wipes
		// its stale positions before seeing the fresh QUOTE against the
		// reset price.
		for _, dgram := range resolvedDgrams {
			_ = entry.wtSession.SendDatagram(dgram)
		}
		for _, dgram := range quoteDgrams {
			_ = entry.wtSession.SendDatagram(dgram)
		}
	}
}
