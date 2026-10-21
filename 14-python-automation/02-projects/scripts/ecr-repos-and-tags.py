"""
List ECR repositories and image tags

- Get all the repositories in ECR
- Print the name of each repository
- Choose one specific repository, and for that repository list all the image tags inside, sorted by date, with the most recent image tag on top

"""

import boto3

ecr_client = boto3.client("ecr")

def get_all_repos():
    response = ecr_client.describe_repositories()
    repos = response["repositories"]
    repo_list = []
    for repo in repos:
        repo_list.append(repo["repositoryName"])
    return repo_list

def sort_images(repo_name):
    response = ecr_client.describe_images(repositoryName=repo_name, filter={"tagStatus":"TAGGED"})
    images = response["imageDetails"]
    image_list=[]
    for image in images:
        image_tags=image["imageTags"]
        push_date = image["imagePushedAt"]
        image_list.append({"Tags":image_tags,"Date pushed":push_date})
    
    print(f"\nImages in repository: {repo_name}")
    for i in sorted(image_list, key=lambda date: date["Date pushed"], reverse=True): print(f"Tags: {i["Tags"]} Date pushed: {i["Date pushed"].strftime("%Y-%m-%d %H:%M:%S")}")
    
    
repos_list = get_all_repos()
for i in repos_list: print(f"Repo name: {i}")
sort_images(repos_list[0])