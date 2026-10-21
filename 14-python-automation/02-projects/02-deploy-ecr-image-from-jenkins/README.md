# Deploy an ECR image to EC2 from a Jenkins pipeline with Python

**Technologies:** Python, boto3, paramiko, requests, Jenkins (declarative pipeline, `input` step, credentials), AWS (ECR, EC2), Docker, nginx

A Jenkins pipeline deploys an image from ECR to an EC2 server. It lists the image tags in the ECR repository, lets the user choose one in the Jenkins UI, logs in to ECR on the server, starts the container from the selected image and checks that the selected version is really running. Jenkins only orchestrates; every step that talks to AWS or the server is a Python script.

## How it works

```
 Jenkins                                                            EC2 (Amazon Linux 2023, Docker)
 ┌───────────────────────────────────────────────────────┐
 │ 1. Fetch Images   (fetch_images.py)                   │
 │      boto3 → ECR describe_images → tags, newest first │
 │      stdout ──returnStdout──> env.IMAGE_TAGS          │
 │                                                       │
 │ 2. Select version Jenkins input (choice)              │
 │      user picks a tag ──> env.IMAGE_TAG               │
 │                                                       │
 │ 3. Deploy         (deploy.py)                         │
 │      boto3 → ECR get_authorization_token              │
 │      paramiko SSH ───────────────────────────────────────>  docker login (password via stdin)
 │                    ───────────────────────────────────────>  docker rm -f nginx-app
 │                    ───────────────────────────────────────>  docker run -d -p 8080:80 <image>:<tag>
 │                                                       │
 │ 4. Validate       (validate.py)                       │
 │      GET http://<ec2>:8080 ──────────────────────────────>  "nginx-app version <tag>"
 │      200 + selected tag in page → pass, else exit 1   │
 └───────────────────────────────────────────────────────┘
```

| File | What it does |
|---|---|
| `Jenkinsfile` | Four stages: fetch tags, let the user choose one with an `input` step, deploy, validate. |
| `fetch_images.py` | Gets the tagged images of `REPO_NAME`, sorts them newest first and prints only the tags, one per line. |
| `deploy.py` | Gets an ECR token, connects to EC2 over SSH, logs in to ECR, replaces the `nginx-app` container with the selected image. Exits with `1` if any command fails. |
| `validate.py` | Requests `http://<ec2>:8080` up to 5 times, 5 seconds apart. Passes only if the status is `200` and the page contains the selected tag. |

All values come from environment variables (`REPO_NAME`, `EC2_HOST`, `APP_PORT`, `IMAGE_TAG`, `SSH_USER`, `SSH_KEY_FILE`), so the scripts have nothing hardcoded and can also be run locally by exporting them.

### Decisions

- **Python → Jenkins via stdout.** The tags travel as stdout → `env.IMAGE_TAGS` → `input` → `env.IMAGE_TAG` → the next scripts read it from the environment. `fetch_images.py` prints nothing else, because every stdout line becomes a choice. The newest tag comes first, so it is the default in the dropdown.
- **No secrets in code or on disk.** AWS keys come from Jenkins credentials as `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`, which boto3 reads automatically. The SSH key is a Jenkins "SSH Username with private key" credential.
- **The server needs no AWS credentials.** Jenkins gets the ECR token and passes it over SSH. `docker login --password-stdin` gets the password through stdin, so it never appears on the command line or in logs.
- **Validation checks the version, not only the status.** Each test image serves a page with its own tag, so a `200` from an old container would not pass.
- **Exit codes drive the pipeline.** Each script exits with `1` on failure, and the `sh` step fails the stage.

## Requirements

- An ECR repository (`nginx-app`) with tagged images that each serve a page containing their tag
- An EC2 instance with Docker, port 8080 open, reachable over SSH from Jenkins
- Jenkins with Python 3, `boto3`, `paramiko` and `requests`
- Jenkins credentials: `jenkins_aws_access_key_id`, `jenkins_aws_access_secret_key` and `ec2-python-key` (SSH Username with private key)
- A Pipeline job with Script Path `14-python-automation/02-projects/02-deploy-ecr-image-from-jenkins/Jenkinsfile`, with `EC2_HOST` in the Jenkinsfile set to the server's IP

## Usage

**Build** the job, pick a tag when the pipeline asks for input, and open `http://<ec2>:8080`.

## Result

The pipeline listed three tags, deployed the selected `3.0` and confirmed that this version was running:

```
[Pipeline] { (Fetch Images)
Available tags:
3.0
2.0
1.0
[Pipeline] { (Select version)
Approved by emre
selected: 3.0
[Pipeline] { (Deploy with python)
Logged in to ECR
Container started from <account-id>.dkr.ecr.eu-central-1.amazonaws.com/nginx-app:3.0
[Pipeline] { (Validate)
App is running: nginx-app version 3.0
Finished: SUCCESS
```
