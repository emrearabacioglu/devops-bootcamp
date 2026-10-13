# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## API Request to GitLab

### Demo Executed: Listing Public Repositories via the GitHub API

I used the GitHub API instead of GitLab.

#### API Request with requests
Sent a GET request to the GitHub REST API, parsed the JSON response and printed the name and URL of every public repository of my user.

```python
    import requests

    response = requests.get("https://api.github.com/users/emrearabacioglu/repos")
    my_repos = response.json()

    for repo in my_repos:
        print(f"Repository Name: {repo['name']}\nRepository Url: {repo['html_url']}\n")
```

#### Execution
Output lists every public repo with its URL:
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/apirequest.py
    Repository Name: aws-exercises
    Repository Url: https://github.com/emrearabacioglu/aws-exercises

    Repository Name: cloud-exercises
    Repository Url: https://github.com/emrearabacioglu/cloud-exercises

    Repository Name: devops-bootcamp
    Repository Url: https://github.com/emrearabacioglu/devops-bootcamp

    Repository Name: devops-case
    Repository Url: https://github.com/emrearabacioglu/devops-case

    Repository Name: docker-exercises
    Repository Url: https://github.com/emrearabacioglu/docker-exercises

    Repository Name: java-app-chart
    Repository Url: https://github.com/emrearabacioglu/java-app-chart

    Repository Name: java-maven-app
    Repository Url: https://github.com/emrearabacioglu/java-maven-app

    Repository Name: java-terraform
    Repository Url: https://github.com/emrearabacioglu/java-terraform

    Repository Name: jenkins-exercises
    Repository Url: https://github.com/emrearabacioglu/jenkins-exercises

    Repository Name: jenkins-shared-library
    Repository Url: https://github.com/emrearabacioglu/jenkins-shared-library

    Repository Name: js-app
    Repository Url: https://github.com/emrearabacioglu/js-app

    Repository Name: terraform
    Repository Url: https://github.com/emrearabacioglu/terraform
```
