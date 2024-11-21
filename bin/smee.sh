#!/bin/bash

# Check if smee is installed
if ! command -v smee &> /dev/null
then
    echo "smee-client could not be found, installing..."
    npm install --global smee-client
fi

# Start smee
smee --url https://smee.io/NP59jhHPw2Ujd2ML --target http://localhost:8000/webhooks/github/123/handle

