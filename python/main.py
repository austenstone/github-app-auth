import datetime
import os
import sys

import requests
import jwt

gh_app_id = os.getenv('GITHUB_APP_ID')
gh_app_key = os.getenv('GITHUB_PRIVATE_KEY_PATH') or 'private-key.pem'
gh_app_inst_id = os.getenv('GITHUB_INSTALLATION_ID')

# read the app_key from file private-key.pem if it doesn't exist in the env variables
if not gh_app_key:
    with open('private-key.pem', 'r') as key_file:
        gh_app_key = key_file.read()

if __name__ == "__main__":
    if not gh_app_id:
        sys.exit("GH_APP_ID is not set")
    if not gh_app_key:
        sys.exit("GH_APP_KEY is not set")

    with open(gh_app_key, "r") as key_file:
        key = key_file.read()

    now = int(datetime.datetime.now().timestamp())
    payload = {
        "iat": now - 60,
        "exp": now + 60 * 8,  # expire after 8 minutes
        "iss": gh_app_id
    }
    encoded = jwt.encode(payload=payload, key=key, algorithm="RS256")

    print('gh_app_inst_id: ', gh_app_inst_id)
    if not gh_app_inst_id:
        # get app installations without installation id
        url = "https://api.github.com/app/installations"
        headers = {
            "Authorization": f"Bearer {encoded}"
        }
        response = requests.get(url, headers=headers)
        # get the first installation id
        gh_app_inst_id = response.json()[0]["id"]
        print('gh_app_inst_id:', gh_app_inst_id)
    else:
        url = f"https://api.github.com/app/installations/{gh_app_inst_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {encoded}"
        }
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
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url, json={"query": query}, headers=headers)
        print('Response:', response.json())
