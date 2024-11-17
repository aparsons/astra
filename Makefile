# Variables
IMAGE_NAME = astra
CONTAINER_NAME = astra
DOCKERFILE_PATH = Dockerfile
DOCKER_COMPOSE_FILE = compose.yml

# Default target
.PHONY: all
all: build

# Build the Docker image
.PHONY: build
build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE_PATH) .

# Run the Docker container
.PHONY: run
run:
	docker run --name $(CONTAINER_NAME) --rm --publish 8000:8000 $(IMAGE_NAME)

# Exec into the running Docker container
.PHONY: exec
exec:
	docker exec -it $(CONTAINER_NAME) /bin/bash

.PHONY: interactive
interactive:
	docker run --name $(CONTAINER_NAME) --rm --interactive --tty --publish 8001:8000 $(IMAGE_NAME) /bin/bash

# Stop the Docker container
.PHONY: stop
stop:
	docker stop $(CONTAINER_NAME)

# Remove the Docker container
.PHONY: rm
rm:
	docker rm $(CONTAINER_NAME)

# View logs from the Docker container
.PHONY: logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Run Docker Compose
.PHONY: compose-up
compose-up:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

# Stop Docker Compose
.PHONY: compose-down
compose-down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# Clean up Docker images and containers
.PHONY: clean
clean:
	docker system prune -f
