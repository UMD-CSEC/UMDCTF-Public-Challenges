.PHONY: build run start

build: Dockerfile
	docker build -t abefleming/aa-express-base .

run:
	docker run -p 3100:3100 -d abefleming/aa-express-base

start: build run
