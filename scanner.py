
import sys
import json
import requests
from datetime import datetime

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

    log_messages = []
    log_messages.append(f"Scanning {target_user}'s repositories for descriptions containing any of {search_terms}...")
    print(f"\n{log_messages[-1]}")

    while True:
        url = f'https://api.github.com/users/{target_user}/repos?type=public&page={page}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_msg = f"Error: Could not fetch repositories for {target_user}. Status code: {response.status_code}"
            print(error_msg)
            log_messages.append(error_msg)
            return found_repos, log_messages

        repos = response.json()
        if not repos:
            break

        for repo in repos:
            description = repo.get('description') or ""
            if any(term.lower() in description.lower() for term in search_terms):
                found_repos.append(repo['html_url'])

        page += 1

    if found_repos:
        success_msg = "Found matches in the following repositories:"
        print(f"\n{success_msg}")
        log_messages.append(success_msg)
        for repo_url in found_repos:
            print(f"- {repo_url}")
            log_messages.append(f"- {repo_url}")
    else:
        no_match_msg = "No repositories matched the search terms."
        print(f"\n{no_match_msg}")
        log_messages.append(no_match_msg)

    return found_repos, log_messages

def write_results(filename, username_logs, affected_count, affected_users):
    with open(filename, 'w') as f:
        for user, logs in username_logs.items():
            for line in logs:
                f.write(line + "\n")
            f.write("\n")
        f.write(f"Total affected users: {affected_count}\n")
        f.write(f"Affected users: {', '.join(affected_users) if affected_users else 'None'}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <target_username> OR python scanner.py -f <file_with_usernames>")
        sys.exit(1)

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

    if response.status_code != 200:
        print(f"\nAuthentication failed. Status code: {response.status_code}")
        sys.exit(1)

    print("\nSuccessfully authenticated.")

    affected_count = 0
    affected_users = []

    if sys.argv[1] == '-f':
        if len(sys.argv) < 3:
            print("Error: Missing file path after -f flag.")
            sys.exit(1)
        file_path = sys.argv[2]
        try:
            with open(file_path, 'r') as f:
                target_users = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

        output_filename = f"github-multi-scan-results{datetime.now().strftime('%Y-%m-%d')}.txt"
        username_logs = {}
        for user in target_users:
            repos, logs = scan_repositories(username, user, search_terms, token)
            username_logs[user] = logs
            if repos:
                affected_count += 1
                affected_users.append(user)
        write_results(output_filename, username_logs, affected_count, affected_users)
        print(f"\nTotal affected users: {affected_count}")
        print(f"Affected users: {', '.join(affected_users) if affected_users else 'None'}")
        print(f"All results saved to {output_filename}")

    else:
        target_user = sys.argv[1]
        repos, logs = scan_repositories(username, target_user, search_terms, token)
        if repos:
            affected_count = 1
            affected_users.append(target_user)
        output_filename = f"github-{target_user}-scan-results{datetime.now().strftime('%Y-%m-%d')}.txt"
        write_results(output_filename, {target_user: logs}, affected_count, affected_users)
        print(f"\nTotal affected users: {affected_count}")
        print(f"Affected users: {', '.join(affected_users) if affected_users else 'None'}")
        print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()