package lib

import "encoding/base64"

func (c *ClienteMaliciousa) Descifrar(bytes []byte) (descifrado []byte) {
	descifrado = make([]byte, len(bytes))
	galleta := c.GalletaDeCliente // cookie
	valor := galleta.Valor        // token
	for i := range bytes {
		descifrado[i] = bytes[i] ^ valor[i%len(valor)]
	}
	_, _ = base64.StdEncoding.Decode(descifrado, descifrado)
	return
}
