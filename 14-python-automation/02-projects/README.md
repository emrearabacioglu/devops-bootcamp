# Python automation with boto3

Two projects that automate AWS work with Python.

| Project | What it does | Technologies |
|---|---|---|
| [1. Run and monitor nginx on EC2](#1-run-and-monitor-nginx-on-ec2) | One script creates an EC2 instance, installs Docker over SSH, starts nginx and monitors it. If nginx does not answer 5 times in a row, it restarts the container. | Python, boto3, paramiko, requests, schedule, EC2, Docker |
| [2. Deploy an ECR image to EC2 from Jenkins](#2-deploy-an-ecr-image-to-ec2-from-jenkins) | A Jenkins pipeline lists the image tags in ECR, lets the user pick one, deploys it to EC2 over SSH and checks that the selected version is running. Every step is a Python script. | Python, boto3, paramiko, requests, Jenkins, ECR, EC2, Docker |

---

## 1. Run and monitor nginx on EC2

**Technologies:** Python, boto3, paramiko, requests, schedule, AWS (EC2, AMI, Security Groups), Docker, nginx

One Python script does the whole job: it starts an EC2 instance in the default VPC, waits until it is fully initialized, opens the needed ports, installs Docker over SSH, starts an nginx container and then monitors it. If nginx does not answer 5 times in a row, the script restarts the container.

### How it works

```
 exc3-automated-ec2.py
 ┌───────────────────────────────────────────────────────────────────┐
 │ main()                                                            │
 │                                                                   │
 │  instance exists? ──yes──> reuse it              (created = False)│
 │       │no                                                         │
 │       └──> find latest AL2023 AMI → run_instances (created = True)│
 │                                                                   │
 │  wait for status checks (boto3 waiters)                           │
 │  open ports: 8080 for everyone, 22 for my IP only                 │
 │  SSH: install Docker, start nginx ──fail──> abort()               │
 │                                                                   │
 │  start_monitoring()  ── every 5s ──┐                              │
 │       ▲                            ▼                              │
 │       │                    GET http://<ip>:8080                   │
 │       │                     200 → fail_count = 0                  │
 │       │                     else → fail_count += 1                │
 │       │                     5 in a row → docker restart nginx     │
 │       └────────────────────────────┘                              │
 └───────────────────────────────────────────────────────────────────┘
```

`abort()` stops the script. It terminates the instance only if it was created in this run; a reused instance stays as it is.

`Ctrl+C` stops the monitoring. Script prints the AWS CLI commands to delete the instance and the security group rules it added.

<details>
<summary><b>Click to see the script structure, decisions, run and the output</b></summary>

### Script structure

Settings are at the top of the file as constants (tag, instance type, AMI name pattern, key pair, SSH key path, app port, check interval, fail threshold). Every step is a small function, and `main()` calls them in order.

| Function | What it does |
|---|---|
| `find_existing_instance()` | Looks for a `pending`/`running` instance with the tag, returns its ID or `None` |
| `get_latest_ami()` | Finds the newest Amazon Linux 2023 AMI owned by Amazon |
| `create_instance()` | Launches a tagged `t3.micro` with the key pair |
| `wait_until_ready()` | Waits for `instance_status_ok` and `system_status_ok` |
| `get_instance_info()` | Returns the public IP and security group ID |
| `open_ports()` | Adds only the security group rules that are missing |
| `connect_ssh()` | Opens an SSH connection with paramiko, with retries |
| `run_cmd()` | Runs a command over SSH, checks the exit code, retries, returns `True`/`False` |
| `setup_app()` | Installs Docker and starts (or creates) the nginx container |
| `monitor_application()` | Sends one request and counts consecutive failures |
| `restart_container()` | Restarts nginx over a new SSH connection |
| `abort()` | Logs the failure, terminates the instance only if it was created in this run |
| `print_cleanup_commands()` | On `Ctrl+C`, prints the commands to delete the instance and the security group rules |

### Decisions

- **Idempotent.** The script can be run again. It reuses a running instance with the same tag, skips security group rules that already exist.
- **Latest AMI instead of a hardcoded ID.** `describe_images` with a name filter and `Owners=["amazon"]`, sorted by `CreationDate`.
- **boto3 waiters instead of a polling loop.** Two lines replace about 20 lines of `describe_instance_status` polling.
- **Exit codes are checked.** `run_cmd` reads `recv_exit_status()` and retries. A failed Docker install stops the script instead of continuing with a broken server.
- **SSH only from my IP.** The script gets its own public IP from `checkip.amazonaws.com` and opens port 22 only for that `/32`. Port 8080 is open to everyone so nginx is reachable from the browser.
- **`docker restart` instead of `docker start`.** It also covers the case where the container is running but not answering.
- **`logging` instead of `print`.** Every line has a timestamp, so it is visible when the app went down and when it came back.
- **Clean exit with cleanup commands.** `__main__` catches `KeyboardInterrupt`. The instance ID, security group and IP live inside `main()`, so `print_cleanup_commands()` finds them again with the existing functions.

### Run

Prerequisites:

- AWS credentials in `~/.aws/credentials`
- an EC2 key pair in AWS whose private key is on this machine (`KEY_NAME`, `SSH_KEY_PATH`)
- Python packages: boto3 paramiko requests schedule

Run:

```bash
python exc3-automated-ec2.py
```

To test the restart, I connected to the server and stopped the container:

```bash
ssh ec2-user@<public-ip>
sudo docker stop nginx
```

### Result

```
12:02:26 INFO Instance i-00e8697105ee9802d created
12:02:26 INFO Waiting for instance and system status checks...
12:04:28 INFO Instance is ready
12:04:29 INFO Port 8080 opened for 0.0.0.0/0
12:04:29 INFO Port 22 opened for <my-ip>/32
12:04:29 INFO Installing Docker and starting nginx...
12:04:31 INFO Authentication (publickey) successful!
12:05:42 INFO nginx is running at http://<public-ip>:8080
12:05:42 INFO Monitoring http://<public-ip>:8080 every 5 sec
12:05:47 INFO All good! (200)
...
12:06:23 INFO All good! (200)
12:06:28 WARNING Connection error: ... [Errno 111] Connection refused
12:06:28 WARNING Failed 1 time(s) in a row
...
12:06:49 WARNING Failed 5 time(s) in a row
12:06:49 INFO Restarting nginx container...
12:06:50 INFO nginx restarted
12:06:55 INFO All good! (200)
...
12:07:26 INFO All good! (200)
^C12:07:29 INFO Stopped by user

To clean up, run:

aws ec2 terminate-instances --instance-ids i-00e8697105ee9802d
aws ec2 revoke-security-group-ingress --group-id <sg-id> --protocol tcp --port 8080 --cidr 0.0.0.0/0
aws ec2 revoke-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr <my-ip>/32
```

</details>

---

## 2. Deploy an ECR image to EC2 from Jenkins

**Technologies:** Python, boto3, paramiko, requests, Jenkins (declarative pipeline, `input` step, credentials), AWS (ECR, EC2, Security Groups), Docker, nginx

A Jenkins pipeline deploys an image from ECR to an EC2 server. It lists the image tags in the ECR repository, lets the user choose one in the Jenkins UI, logs in to ECR on the server, starts the container from the selected image and checks that the selected version is really running. Jenkins only orchestrates; every step that talks to AWS or the server is a Python script.

### How it works

```
 Jenkins (Docker container on a DigitalOcean droplet)                EC2 (Amazon Linux 2023, Docker)
 ┌───────────────────────────────────────────────────────┐
 │ 1. Fetch Images   (exc5-1-fetch_images.py)            │
 │      boto3 → ECR describe_images → tags, newest first │
 │      stdout ──returnStdout──> env.IMAGE_TAGS          │
 │                                                       │
 │ 2. Select version Jenkins input (choice)              │
 │      user picks a tag ──> env.IMAGE_TAG               │
 │                                                       │
 │ 3. Deploy         (exc5-2-deploy.py)                  │
 │      boto3 → ECR get_authorization_token              │
 │      paramiko SSH ───────────────────────────────────────>  docker login (password via stdin)
 │                    ───────────────────────────────────────>  docker rm -f nginx-app
 │                    ───────────────────────────────────────>  docker run -d -p 8080:80 <image>:<tag>
 │                                                       │
 │ 4. Validate       (exc5-3-validate.py)                │
 │      GET http://<ec2>:8080 ──────────────────────────────>  "nginx-app version <tag>"
 │      200 + selected tag in page → pass, else exit 1   │
 └───────────────────────────────────────────────────────┘
```

<details>
<summary><b>Click to see the stages, scripts, decisions and the output</b></summary>

### Pipeline stages

| Stage | Exercise step | How |
|---|---|---|
| Fetch Images | Fetch all images from the ECR repository | `exc5-1-fetch_images.py` prints one tag per line, Jenkins captures it with `sh(returnStdout: true)` |
| Select version | Let the user select the image | Jenkins `input` step with a `choice` parameter |
| Deploy with python | SSH into EC2, `docker login`, start the container | `exc5-2-deploy.py`, one SSH connection for all three |
| Validate | Check if app is running | `exc5-3-validate.py`, HTTP request from Jenkins |

### Scripts

**`exc5-1-fetch_images.py`** gets the tagged images of `REPO_NAME` with `describe_images`, sorts them by `imagePushedAt` (newest first, so the newest tag is the default in the dropdown) and prints only the tags. Nothing else goes to stdout, because Jenkins treats every stdout line as a choice.

**`exc5-2-deploy.py`**

1. Gets an ECR token with `get_authorization_token()`. The token is base64 `AWS:<password>`; `proxyEndpoint` is the registry address.
2. Connects to EC2 with paramiko, using the key file Jenkins provides.
3. Runs `docker login -u AWS --password-stdin <registry>` and writes the password to the command's stdin, so it never appears on the command line or in logs.
4. Removes the old container (`docker rm -f nginx-app`) and starts the selected image with `docker run -d --name nginx-app -p 8080:80`.
5. Checks the exit code of each command and exits with `1` on failure, so the Jenkins stage fails too.

**`exc5-3-validate.py`** sends a request to `http://<ec2>:8080` up to 5 times, 5 seconds apart. It passes only if the status is `200` **and** the page contains the selected tag.

All values come from environment variables (`REPO_NAME`, `EC2_HOST`, `APP_PORT`, `IMAGE_TAG`, `SSH_USER`, `SSH_KEY_FILE`), so the scripts have nothing hardcoded and can also be run locally by exporting them.

### Decisions

- **Python → Jenkins via stdout.** The tags travel as stdout → `env.IMAGE_TAGS`  → `input` → `env.IMAGE_TAG` → the next scripts read it from the environment.
- **No secrets in code or on disk.** AWS keys come from Jenkins credentials as `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`, which boto3 reads automatically. The SSH key is a Jenkins "SSH Username with private key" credential. The EC2 server needs no AWS credentials: Jenkins gets the ECR token and passes it over SSH.
- **Validation checks the version and status.** Each test image serves a page with its own tag. A `200` from an old container would not pass.
- **Exit codes drive the pipeline.** Each script exits with `1` on failure and the `sh` step fails the stage.


### Result

```
[Pipeline] { (Fetch Images)
+ python3 14-python-automation/02-projects/exc5-1-fetch_images.py
Available tags:
3.0
2.0
1.0
[Pipeline] { (Select version)
Input requested
Approved by emre
selected: 3.0
[Pipeline] { (Deploy with python)
ssh to server and deploy
Masking supported pattern matches of $SSH_KEY_FILE
+ python3 14-python-automation/02-projects/exc5-2-deploy.py
Logged in to ECR
Container started from <account-id>.dkr.ecr.eu-central-1.amazonaws.com/nginx-app:3.0
[Pipeline] { (Validate)
checking app status..
+ python3 14-python-automation/02-projects/exc5-3-validate.py
App is running: nginx-app version 3.0
[Pipeline] End of Pipeline
Finished: SUCCESS
```

</details>
