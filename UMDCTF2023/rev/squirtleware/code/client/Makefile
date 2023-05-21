GOOS		:= linux
GOARCH		:= amd64

all:
	@mkdir -p build
	cd cmd/squirtleware && GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o ../../build/squirtleware

clean:
	@rm -rf build/**