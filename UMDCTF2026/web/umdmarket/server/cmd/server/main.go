package main

import (
	"flag"
	"log"
	"os"

	"predictionmarket/internal/server"
)

func main() {
	addr := flag.String("addr", ":4443", "listen address")
	certPath := flag.String("cert", "/app/cert.pem", "PEM-encoded leaf certificate")
	keyPath := flag.String("key", "/app/key.pem", "PEM-encoded private key")
	flag.Parse()

	flagValue := os.Getenv("FLAG")
	if flagValue == "" {
		log.Fatal("FLAG environment variable is required")
	}

	srv := server.New(flagValue)
	if err := srv.ListenAndServe(*addr, *certPath, *keyPath); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
