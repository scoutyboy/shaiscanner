
import requests
import sys
import json

def load_config(config_path="config.json"):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)

def scan_repositories(username, target_user, search_terms, token):
    page = 1
    found_repos = []
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': username
    }

    print(f"\nScanning {target_user}'s repositories for descriptions containing any of {search_terms}...")

    while True:
        url = f'https://api.github.com/users/{target_user}/repos?type=public&page={page}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: Could not fetch repositories for {target_user}. Status code: {response.status_code}")
            return

        repos = response.json()
        if not repos:
            break

        for repo in repos:
            description = repo.get('description') or ""
            if any(term.lower() in description.lower() for term in search_terms):
                found_repos.append(repo['html_url'])

        page += 1

    if found_repos:
        print("\nFound matches in the following repositories:")
        for repo_url in found_repos:
            print(f"- {repo_url}")
    else:
        print("\nNo repositories matched the search terms.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <target_username>")
        sys.exit(1)

    target_user = sys.argv[1]
    config = load_config()

    username = config.get("username")
    token = config.get("token")
    search_terms = config.get("search_terms")

    if not all([username, token, search_terms]):
        print("Error: Missing required fields in config file.")
        sys.exit(1)

    # Authentication check
    auth_check_url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {token}', 'User-Agent': username}
    response = requests.get(auth_check_url, headers=headers)

    if response.status_code == 200:
        print(f"\nSuccessfully authenticated.")
        scan_repositories(username, target_user, search_terms, token)
    else:
        print(f"\nAuthentication failed. Status code: {response.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    main()
