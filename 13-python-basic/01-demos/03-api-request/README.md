# API Request to GitLab

**Technologies:** Python, GitHub API, VS Code, Git

A Python script that talks to the API of an external application and lists all public repositories of a user. I used the GitHub API instead of GitLab, the logic is the same.

## Summary
- `apirequest.py` sends a GET request to `https://api.github.com/users/emrearabacioglu/repos` with the `requests` package.
- The JSON response is parsed with `response.json()`.
- For each repository the script prints the name and the URL (`html_url`).

## Run
```bash
pip install requests
python apirequest.py
```

## Result
Every public repository of my GitHub user with its URL:
```
(.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/apirequest.py
Repository Name: aws-exercises
Repository Url: https://github.com/emrearabacioglu/aws-exercises

Repository Name: cloud-exercises
Repository Url: https://github.com/emrearabacioglu/cloud-exercises

Repository Name: devops-bootcamp
Repository Url: https://github.com/emrearabacioglu/devops-bootcamp
...
Repository Name: terraform
Repository Url: https://github.com/emrearabacioglu/terraform
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
