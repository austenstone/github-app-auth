#!/bin/bash

# Set the App ID and Private Key path
APP_ID=${GITHUB_APP_ID}
PRIVATE_KEY_PATH='private-key.pem'

NOW=$(date +%s)
LATER=$(($NOW + 300))

# Generate the JWT
PAYLOAD=$(printf '{"iat": %d, "exp": %d, "iss": "%d"}' $NOW $LATER $APP_ID)
echo 'PAYLOAD' + $PAYLOAD

JWT=$(echo -n "$PAYLOAD" | openssl dgst -binary -sha256 -sign "$PRIVATE_KEY_PATH" -binary | b64enc)
echo $JWT

curl --request GET \
--url "https://api.github.com/app/installations" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer $JWT"
