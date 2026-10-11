import requests

response = requests.get("https://api.github.com/users/emrearabacioglu/repos")
my_repos = response.json()

for repo in my_repos:
    print(f"Repository Name: {repo['name']}\nRepository Url: {repo['html_url']}\n")