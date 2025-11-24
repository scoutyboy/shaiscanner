import requests
import sys

def scan_repositories(username, target_user, search_string, token):
    """
    Scans a target user's public repositories for a specific string in their descriptions.
    
    Args:
        username (str): The authenticated user's GitHub username.
        target_user (str): The username of the user whose repos will be scanned.
        search_string (str): The string to search for in repository descriptions.
        token (str): The GitHub Personal Access Token for authentication.
    """
    page = 1
    found_repos = []
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': username # GitHub API requires a User-Agent header
    }

    print(f"\nScanning {target_user}'s repositories for descriptions containing '{search_string}'...")

    while True:
        url = f'https://api.github.com/users/{target_user}/repos?type=public&page={page}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: Could not fetch repositories for {target_user}. Status code: {response.status_code}")
            print(response.json())
            return

        repos = response.json()
        if not repos:
            break # No more repositories to check

        for repo in repos:
            description = repo.get('description')
            if description and search_string.lower() in description.lower():
                found_repos.append(repo['html_url'])

        page += 1

    if found_repos:
        print(f"\nFound the string '{search_string}' in the following repository descriptions:")
        for repo_url in found_repos:
            print(f"- {repo_url}")
    else:
        print(f"\nNo repositories found with the string '{search_string}' in their descriptions.")

def main():
    """
    Main function to handle user input and authentication.
    """
    print("GitHub Repository Scanner CLI")
    print("-" * 30)

    username = input("Enter your GitHub username (for API User-Agent): ").strip()
    token = input("Enter your GitHub Personal Access Token (PAT): ").strip()
    target_user = input("Enter the target GitHub username to scan: ").strip()
    search_string = input("Enter the string to search for in descriptions: ").strip()

    if not all([username, token, target_user, search_string]):
        print("Error: All fields are required.")
        sys.exit(1)

    # Simple authentication check (verify the token works)
    auth_check_url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {token}', 'User-Agent': username}
    response = requests.get(auth_check_url, headers=headers)

    if response.status_code == 200:
        print(f"\nSuccessfully authenticated as {response.json()['login']}.")
        scan_repositories(username, target_user, search_string, token)
    else:
        print(f"\nAuthentication failed. Status code: {response.status_code}")
        print("Please check your username and PAT.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
        sys.exit(0)
