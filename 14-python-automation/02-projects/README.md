# Python automation with boto3

Projects that automate AWS work with Python.

| Project | What it does | Technologies |
|---|---|---|
| [Run and monitor nginx on EC2](./01-run-and-monitor-nginx-on-ec2) | One script creates an EC2 instance, installs Docker over SSH, starts nginx and monitors it. If nginx does not answer 5 times in a row, it restarts the container. | Python, boto3, paramiko, requests, schedule, EC2, Docker |
| [Deploy an ECR image to EC2 from Jenkins](./02-deploy-ecr-image-from-jenkins) | A Jenkins pipeline lists the image tags in ECR, lets the user pick one, deploys it to EC2 over SSH and checks that the selected version is running. Every step is a Python script. | Python, boto3, paramiko, requests, Jenkins, ECR, EC2, Docker |

Smaller boto3 scripts in [`scripts/`](./scripts):

| Script | What it does |
|---|---|
| `list-subnets.py` | Lists the subnets in the default region with their Availability Zones. |
| `iam-last-active-user.py` | Lists the IAM users with their last activity and prints the most recently active one. |
| `ecr-repos-and-tags.py` | Lists the ECR repositories and the image tags of one repository, newest first. |
