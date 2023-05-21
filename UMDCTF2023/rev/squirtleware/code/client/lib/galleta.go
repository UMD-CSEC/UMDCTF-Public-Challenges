package lib

import (
	"net/http"
)

type Galleta struct {
	LLave string // key
	Valor string // value
}

func (g *Galleta) SitioWebGalleta() *http.Cookie {
	return &http.Cookie{
		Name:  g.LLave,
		Value: g.Valor,
	}
}
