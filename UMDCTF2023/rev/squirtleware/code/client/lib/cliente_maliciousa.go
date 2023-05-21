package lib

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"gopkg.in/h2non/gentleman.v2"
	"sync"
)

const (
	HomePath = "/squirtle"
	Loml     = "shakira"
)

type ClienteMaliciousa struct {
	Cliente          *gentleman.Client
	SecretoId        int // GRAN SECRETO!!!
	GalletaDeCliente *Galleta
	Mu               *sync.Mutex
}

func (c *ClienteMaliciousa) Url(url string) *ClienteMaliciousa {
	c.Cliente.URL(url)
	return c
}

func (c *ClienteMaliciousa) Pedido() *gentleman.Request {
	return c.Cliente.Request().AddCookie(c.GalletaDeCliente.SitioWebGalleta())
}

func (c *ClienteMaliciousa) Acceso(url, user string) *ClienteMaliciousa {
	userObject := struct {
		Name string `json:"name"`
		Node int    `json:"node"`
	}{
		Name: user,
		Node: c.SecretoId,
	}
	req := c.Url(url + HomePath + "/i-love-" + Loml).Cliente.Request()
	req.Method("POST")
	req.JSON(userObject)
	resp, err := req.Do()
	if err != nil {
		return c
	}

	token := &struct {
		Token string `json:"token"`
	}{}
	if json.Unmarshal(resp.Bytes(), token) != nil {
		panic("uff")
	}
	c.GalletaDeCliente = &Galleta{
		LLave: "token",
		Valor: token.Token,
	}
	return c
}

func (c *ClienteMaliciousa) ObtenerBandera(url string, data string) (b *Bandera, err error) {
	opts := struct {
		Type string `json:"type"`
		Data string `json:"data"`
	}{
		Type: "BANDERA_POR_FAVOR", // hmmmm
	}
	opts.Data = base64.StdEncoding.EncodeToString([]byte(data))
	opts.Data = opts.Data[:len(opts.Data)]
	fmt.Println(opts.Data)
	resp, err := c.Pedido().URL(url + "/connection").Method("POST").JSON(opts).Do()
	if err != nil {
		fmt.Println(err.Error())
		return nil, err
	}
	if resp.RawResponse.StatusCode != 200 {
		// Went wrong
		fmt.Printf("aye %d\n", resp.RawResponse.StatusCode)
	}
	ses := len("squirtleenespanol")
	respBytes := resp.Bytes()
	respBytes = respBytes[ses:]
	respBytes = respBytes[8:] // padding
	respBytes = respBytes[0 : len(respBytes)-(ses+8-1)]
	b = &Bandera{
		Contenido: respBytes,
	}
	return
}

func (c *ClienteMaliciousa) CerrarSesion(url string) (str string, err error) {
	req := c.Url(url + HomePath + "/bye").Pedido().AddCookie(c.GalletaDeCliente.SitioWebGalleta()).Method("POST")
	resp, err := req.Do()
	if err != nil {
		return "", err
	}
	return string(resp.Bytes()), err
}
