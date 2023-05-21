package main

import (
	"ctf.malware.wtf/squirtleware/lib"
	"flag"
	"fmt"
	"gopkg.in/h2non/gentleman.v2"
	"os"
	"sync"
)

const (
	SecretoId = 420
)

var (
	user = flag.String("name", "squirtlesquadup", "who are you?")
	url  = flag.String("url", "localhost:8080", "url")
)

func init() {
	flag.Parse()
}

func main() {

	cliente := &lib.ClienteMaliciousa{
		Cliente:          gentleman.New(),
		SecretoId:        SecretoId,
		Mu:               &sync.Mutex{},
		GalletaDeCliente: &lib.Galleta{},
	}
	req := cliente.Acceso(*url, *user)
	defer func() {
		out, _ := req.CerrarSesion(*url)
		fmt.Println(out)
		fmt.Println("pide la bandera completa por favor?")
	}()
	fmt.Printf("inicia sesión con token: %#v\n", cliente.GalletaDeCliente.SitioWebGalleta().String())
	req.Pedido().URL(*url)
	bandera, err := req.ObtenerBandera(*url, "bandera")
	if err != nil {
		return
	}
	_ = cliente.Descifrar(bandera.Contenido) // ????
	_ = os.WriteFile("bandera.png", bandera.Contenido, 0777)
}
