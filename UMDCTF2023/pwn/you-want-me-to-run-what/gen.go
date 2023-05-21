package main

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"math/rand"
	"time"
)

func generateRandomString() string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	b := make([]byte, 10)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

func checkMD5(hash string) bool {
	firstDigit := hash[0]
	lastDigit := hash[len(hash)-1]
	if firstDigit == '0' && lastDigit == '0' && hash[1] == '0' && hash[2] == '0' && hash[len(hash)-2] == '0' && hash[len(hash)-3] == '0' {
		return true
	}
	return false
}

func main() {
	rand.Seed(time.Now().UnixNano())

	for {
		randomString := generateRandomString()
		randomString = "IPGwZkdRIE"
		randomString = "Ã" + randomString
		fmt.Println([]byte(randomString))
		hashBytes := md5.Sum([]byte(randomString))
		hashString := hex.EncodeToString(hashBytes[:])

		if checkMD5(hashString) {
			fmt.Printf("Random string %s has an MD5 hash with the correct pattern: %s\n", randomString, hashString)
			break
		}
	}
}
