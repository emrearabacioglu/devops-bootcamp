# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create repository on AWS and push to private Docker registry

### Demo Executed: Push a Node.js image to Amazon ECR

#### Overview
Created a private ECR repository (`my-app`), logged Docker in to ECR with the AWS CLI, and pushed two versions of the Node.js app image.

#### Docker Login to ECR
Configured the AWS CLI, then passed the ECR token to `docker login`:

    root@PC:/mnt/c/Users/emrea# aws configure
    AWS Access Key ID [****************6472]: ******
    AWS Secret Access Key [****************VPGR]: ******
    Default region name [eu-central-1]: eu-central-1
    Default output format [json]: json

    root@PC:/mnt/c/Users/emrea# aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded

#### Build, Tag and Push
Version `1.0`. The image is tagged with the full ECR URL before pushing:

    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.0 .
    ...
    root@PC:/mnt/c/Users/emrea# docker tag my-app:1.0 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    root@PC:/mnt/c/Users/emrea# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    ...
    1.0: digest: sha256:6864de50df6c69649d7fad5dbeab0c774ba73873004dfd7d925a9bd831892474 size: 856

Version `1.1`, same steps:

    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.1 .
    ...
    root@PC:/mnt/c/Users/emrea/js-app# docker tag my-app:1.1 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    ...
    1.1: digest: sha256:b66fee87f8f9fd58d93f7b97329648f34b2957975fb0f00e74af64be5c1aab20 size: 856

Both tags in the ECR repository:

<img width="1631" height="624" alt="image" src="https://github.com/user-attachments/assets/4c8b9763-6c25-423c-b4bb-a2d74dfffbbb" />
