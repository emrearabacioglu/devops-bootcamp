# Create repository on AWS and push to private Docker registry

**Technologies:** Docker, Amazon ECR

I created a private Docker repository in Amazon ECR and pushed two versions of my Node.js app image to it. The app is the same Node.js app as in module 7.

## Summary
1. Created a private repository `my-app` in Amazon ECR (region `eu-central-1`).
2. Configured the AWS CLI and logged Docker in to ECR with the token from `aws ecr get-login-password`.
3. Built the image `my-app:1.0`, tagged it with the full ECR repository URL and pushed it.
4. Did the same for version `1.1`. Both tags are now in the repository.

## Run
```bash
aws configure
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com

docker build -t my-app:1.0 .
docker tag my-app:1.0 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
```
Version `1.1` uses the same commands with tag `1.1`.

## Result
Docker logged in to ECR and both versions were pushed:
```
Login Succeeded
...
root@PC:/mnt/c/Users/emrea# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
...
1.0: digest: sha256:6864de50df6c69649d7fad5dbeab0c774ba73873004dfd7d925a9bd831892474 size: 856
...
root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
...
1.1: digest: sha256:b66fee87f8f9fd58d93f7b97329648f34b2957975fb0f00e74af64be5c1aab20 size: 856
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
