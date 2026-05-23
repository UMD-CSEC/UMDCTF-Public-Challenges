// Package certgen generates the self-signed ECDSA P-256 certificate that the
// WebTransport server presents to browsers. The exact template here is
// load-bearing: the SHA-256 hash of the resulting DER encoding must be
// communicated to the browser via `serverCertificateHashes`, and it must come
// out the same whether the cert is generated at build time (cmd/certgen) or
// any other entry point that reuses this package.
package certgen

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/binary"
	"math/big"
	"time"
)

// Validity is the certificate lifetime. 10 days sits safely under the 14-day
// limit WebTransport enforces on self-signed hashes.
const Validity = 10 * 24 * time.Hour

// Result bundles everything a caller might want: the parsed tls.Certificate
// (ready to hand to a TLS config), the DER leaf (for hash computation or
// PEM encoding), and the ECDSA private key (for PEM encoding).
type Result struct {
	TLS  *tls.Certificate
	Leaf *x509.Certificate
	Key  *ecdsa.PrivateKey
}

// Generate produces a fresh self-signed ECDSA P-256 certificate suitable for
// WebTransport's serverCertificateHashes. The template matches the approach
// from webtransport-go/interop, which is tested against Chrome.
func Generate() (*Result, error) {
	key, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return nil, err
	}

	b := make([]byte, 8)
	if _, err := rand.Read(b); err != nil {
		return nil, err
	}
	serial := int64(binary.BigEndian.Uint64(b))
	if serial < 0 {
		serial = -serial
	}

	now := time.Now()
	tmpl := &x509.Certificate{
		SerialNumber:          big.NewInt(serial),
		Subject:               pkix.Name{},
		NotBefore:             now,
		NotAfter:              now.Add(Validity),
		IsCA:                  true,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth, x509.ExtKeyUsageServerAuth},
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageCertSign,
		BasicConstraintsValid: true,
	}

	certDER, err := x509.CreateCertificate(rand.Reader, tmpl, tmpl, &key.PublicKey, key)
	if err != nil {
		return nil, err
	}
	leaf, err := x509.ParseCertificate(certDER)
	if err != nil {
		return nil, err
	}

	return &Result{
		TLS: &tls.Certificate{
			Certificate: [][]byte{certDER},
			PrivateKey:  key,
			Leaf:        leaf,
		},
		Leaf: leaf,
		Key:  key,
	}, nil
}

// Hash returns the SHA-256 hash of the DER-encoded certificate that browsers
// expect in serverCertificateHashes.
func Hash(leaf *x509.Certificate) [sha256.Size]byte {
	return sha256.Sum256(leaf.Raw)
}
