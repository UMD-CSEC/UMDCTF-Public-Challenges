// certgen emits the self-signed ECDSA certificate used by the WebTransport
// server along with its SHA-256 hash. Intended to run at image-build time so
// the server binary and the frontend bundle can share the same cert bytes.
//
//	certgen -out /certs
//
// Produces:
//
//	/certs/backend-cert.pem   — PEM-encoded leaf certificate
//	/certs/backend-key.pem    — PEM-encoded EC private key (SEC1)
//	/certs/backend-cert.hash  — hex-encoded SHA-256 of the DER certificate (single line, no newline)
package main

import (
	"crypto/x509"
	"encoding/hex"
	"encoding/pem"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"predictionmarket/internal/certgen"
)

func main() {
	out := flag.String("out", ".", "directory to write backend-cert.pem, backend-key.pem, backend-cert.hash into")
	flag.Parse()

	if err := os.MkdirAll(*out, 0o755); err != nil {
		log.Fatalf("mkdir %s: %v", *out, err)
	}

	res, err := certgen.Generate()
	if err != nil {
		log.Fatalf("generate: %v", err)
	}

	certPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "CERTIFICATE",
		Bytes: res.Leaf.Raw,
	})
	if err := writeFile(filepath.Join(*out, "backend-cert.pem"), certPEM, 0o644); err != nil {
		log.Fatalf("write backend-cert.pem: %v", err)
	}

	keyDER, err := x509.MarshalECPrivateKey(res.Key)
	if err != nil {
		log.Fatalf("marshal key: %v", err)
	}
	keyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "EC PRIVATE KEY",
		Bytes: keyDER,
	})
	if err := writeFile(filepath.Join(*out, "backend-key.pem"), keyPEM, 0o600); err != nil {
		log.Fatalf("write backend-key.pem: %v", err)
	}

	sum := certgen.Hash(res.Leaf)
	hashHex := hex.EncodeToString(sum[:])
	if err := writeFile(filepath.Join(*out, "backend-cert.hash"), []byte(hashHex), 0o644); err != nil {
		log.Fatalf("write backend-cert.hash: %v", err)
	}

	fmt.Printf("wrote %s (SHA-256=%s, valid until %s)\n", *out, hashHex, res.Leaf.NotAfter.Format("2006-01-02 15:04:05 MST"))
}

func writeFile(path string, data []byte, mode os.FileMode) error {
	return os.WriteFile(path, data, mode)
}
