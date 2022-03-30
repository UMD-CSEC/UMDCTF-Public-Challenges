package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"errors"
	"fmt"
	"os"
)

/* env GOOS=linux GOARCH=s390x go build source.go */
func main() {
	/* If it finds the .dockerenv file, then error out */
	if _, err := os.Stat(secretStash(1)); err == nil {

		/* This is a dumb check, you can bypass with
		   1) removing the dockerenv file
		   2) patching the bin and skipping the check
		   3) running in a non-docker emulator
		   4) ... plenty of other stuff
		*/
		fmt.Println("Lol nah... I don't do this fake stuff :)")
		os.Exit(69)

		/* In this case, it didn't find anything */
	} else if errors.Is(err, os.ErrNotExist) {
		fmt.Println("Okay, looks good to me!")
	} else {
		fmt.Println("AHHHHH what???")
	}
//	StringToEncrypt := "UMDCTF{g3t_l0st_h0m13}"

	// To encrypt the StringToEncrypt
//	encText, err := Encrypt(StringToEncrypt, MySecret)
//	if err != nil {
//		fmt.Println("error encrypting your classified text: ", err)
//	}
//decText, err := Decrypt("RG5D7AtHRuoEbNk=", MySecret)

//	fmt.Println(encText)
fmt.Println(secretStash(2))
//fmt.Println("Nothing to see here. Go away.")
}

var bytes = []byte{35, 46, 57, 24, 85, 35, 24, 74, 87, 35, 88, 98, 66, 32, 14, 05}

const MySecret string = "abc&1*~#^2^#s0^=)^^7%b34"

func Encode(b []byte) string {
	return base64.StdEncoding.EncodeToString(b)
}

func Decode(s string) []byte {
	data, err := base64.StdEncoding.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return data
}

func Encrypt(text, MySecret string) (string, error) {
	block, err := aes.NewCipher([]byte(MySecret))
	if err != nil {
		return "", err
	}
	plainText := []byte(text)
	cfb := cipher.NewCFBEncrypter(block, bytes)
	cipherText := make([]byte, len(plainText))
	cfb.XORKeyStream(cipherText, plainText)
	return Encode(cipherText), nil
}

func Decrypt(text, MySecret string) (string, error) {
	block, err := aes.NewCipher([]byte(MySecret))
	if err != nil {
		return "", err
	}
	cipherText := Decode(text)
	cfb := cipher.NewCFBDecrypter(block, bytes)
	plainText := make([]byte, len(cipherText))
	cfb.XORKeyStream(plainText, cipherText)
	return string(plainText), nil
}

/* A place to store strings that are encrypted */
func secretStash(hehe int) string {

	/* Create the vault */
	s := make([]string, 1)
	s = append(s, "RG5D7AtHRuoEbNk=") // /.dockerenv
	s = append(s, "By9LowBFA+0TIsj2Zz2ND00v0PSV0+pY") // troll string
	s = append(s, "Pg1jwDxqWP9SdvD/IzqQPvoAHjGlFQ==")  
	ret, err := Decrypt(s[hehe], MySecret)
	if err != nil {}
	return string(ret)

}

