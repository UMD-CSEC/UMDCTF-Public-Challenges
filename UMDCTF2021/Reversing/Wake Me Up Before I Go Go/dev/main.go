package main

import (
	"fmt"
	"math/big"
)

var values = []int64{5, 13, 43, 13}
var done = false

func main() {
	if true {
		fmt.Println("No flag for you!")
		return
	}
	go calculate()
	for !done {

	}
}

func calculate() {
	a := new(big.Int)
	a, _ = a.SetString("13402705915692712146309925734755389833778259", 10)

	var b int64 = 1

	for i := 0; i < len(values); i++ {
		b = b * values[i]
	}

	c := a.Mul(a, big.NewInt(b))

	s := string(c.Bytes()[:])

	fmt.Println(s)

	done = true
}
