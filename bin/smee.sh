#!/bin/bash

docker run --rm --interactive --tty --name smee-client \
  deltaprojects/smee-client \
  --url https://smee.io/NP59jhHPw2Ujd2ML \
  --target http://localhost:8000/webhooks/123/handle
