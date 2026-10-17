import boto3
import os

REPO_NAME=os.environ["REPO_NAME"]
ecr_client = boto3.client("ecr")

def fetch_images(repo_name):
    response = ecr_client.describe_images(repositoryName=repo_name, filter={"tagStatus":"TAGGED"})
    images = sorted(response["imageDetails"], key=lambda i: i["imagePushedAt"], reverse=True)
    image_list=[]
    for image in images:
        image_list.append(image["imageTags"][0])
    return image_list

for i in fetch_images(REPO_NAME): print(i)