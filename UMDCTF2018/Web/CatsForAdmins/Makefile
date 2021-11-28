.PHONY: build run start

build: Dockerfile
	docker build -t abefleming/catsforadmins-express-base .

run:
	docker run -p 3200:3200 -d abefleming/catsforadmins-express-base

start: build run
