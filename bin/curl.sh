#!/bin/bash

WEBHOOKS_URL="http://localhost:8000/webhooks/github/123/handle"

post() {
    curl -X POST -H "Content-Type: application/json" -d '{
        "123-random-uuid": {
            "action": "created"
        }
    }' $WEBHOOKS_URL
}

post
