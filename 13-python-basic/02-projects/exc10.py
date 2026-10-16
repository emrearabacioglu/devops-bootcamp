# Write a program that:

# connects to GitHub API
# gets all the public repositories for a specific GitHub user
# prints the name & URL of every project

import requests

response = requests.get("https://api.github.com/users/emrearabacioglu/repos")
my_repos = response.json()

for repo in my_repos:
    print(f"Repository Name: {repo['name']}\nRepository Url: {repo['html_url']}\n")