#!/bin/bash

# Define the container name
CONTAINER_NAME="smee-client"

# Check if the container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    # Stop the container
    docker stop $CONTAINER_NAME
    echo "Docker container '$CONTAINER_NAME' has been stopped."
else
    echo "Docker container '$CONTAINER_NAME' is not running."
fi
