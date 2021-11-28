.PHONY: build run start

build: Dockerfile
	docker build -t abefleming/robits-express-base .

run:
	docker run -p 3000:3000 -d abefleming/robits-express-base

start: build run
