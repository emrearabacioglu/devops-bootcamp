# Python automation with boto3: Run and monitor nginx on EC2

**Technologies:** Python, boto3, paramiko, requests, schedule, AWS (EC2, AMI, Security Groups), Docker, nginx

One Python script does the whole job: it starts an EC2 instance in the default VPC, waits until it is fully initialized, opens the needed ports, installs Docker over SSH, starts an nginx container and then monitors it. If nginx does not answer 5 times in a row, the script restarts the container.

## How it works

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

## Script structure

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

## Decisions

- **Idempotent.** The script can be run again. It reuses a running instance with the same tag, skips security group rules that already exist.
- **Latest AMI instead of a hardcoded ID.** `describe_images` with a name filter and `Owners=["amazon"]`, sorted by `CreationDate`.
- **boto3 waiters instead of a polling loop.** Two lines replace about 20 lines of `describe_instance_status` polling.
- **Exit codes are checked.** `run_cmd` reads `recv_exit_status()` and retries. A failed Docker install stops the script instead of continuing with a broken server.
- **SSH only from my IP.** The script gets its own public IP from `checkip.amazonaws.com` and opens port 22 only for that `/32`. Port 8080 is open to everyone so nginx is reachable from the browser.
- **`docker restart` instead of `docker start`.** It also covers the case where the container is running but not answering.
- **`logging` instead of `print`.** Every line has a timestamp, so it is visible when the app went down and when it came back.
- **Clean exit with cleanup commands.** `__main__` catches `KeyboardInterrupt`. The instance ID, security group and IP live inside `main()`, so `print_cleanup_commands()` finds them again with the existing functions.

## Run

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

## Result

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
