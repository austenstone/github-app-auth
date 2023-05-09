import os
import sys
import time

import requests
import jwt

app_id = os.getenv('GITHUB_APP_ID')
pem = os.getenv('GITHUB_PRIVATE_KEY_PATH') or (sys.argv[1] if len(sys.argv) > 1 else None) or 'private-key.pem'
install_id = os.getenv('GITHUB_INSTALLATION_ID')

# read the app_key from file private-key.pem if it doesn't exist in the env variables
if not pem:
    with open('private-key.pem', 'r') as key_file:
        pem = key_file.read()

if __name__ == "__main__":
    if not app_id:
        sys.exit("GH_APP_ID is not set")
    if not pem:
        sys.exit("pem is not set")

    # Open PEM
    with open(pem, 'rb') as pem_file:
        signing_key = jwt.jwk_from_pem(pem_file.read())

    payload = {
        # Issued at time
        'iat': int(time.time()),
        # JWT expiration time (10 minutes maximum)
        'exp': int(time.time()) + 600,
        # GitHub App's identifier
        'iss': app_id
    }

    # Create JWT
    jwt_instance = jwt.JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

    print(f"JWT:  {encoded_jwt}")

    # Go get the installation id if we don't have it
    if not install_id:
        url = "https://api.github.com/app/installations"
        headers = { "Authorization": f"Bearer {encoded_jwt}" }
        response = requests.get(url, headers=headers)

        install_id = response.json()[0]["id"]
        print('install_id:', install_id)
    
    # Now we are authenticated as the app, but we need to authenticate as an installation
    url = f"https://api.github.com/app/installations/{install_id}/access_tokens"
    headers = { "Authorization": f"Bearer {encoded_jwt}" }
    response = requests.post(url, headers=headers)
    token = response.json()["token"]
    print('Response:', response.json())

    query = """
    query {
        viewer {
            login
        }
    }
    """
    url = "https://api.github.com/graphql"
    headers = { "Authorization": f"Bearer {token}" }
    response = requests.post(url, json={"query": query}, headers=headers)
    print('Response:', response.json())
