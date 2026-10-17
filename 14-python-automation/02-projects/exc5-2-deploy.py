import sys
import os

import boto3
import paramiko
import base64

SSH_USER = os.environ["SSH_USER"]
SSH_KEY_FILE = os.environ["SSH_KEY_FILE"]
HOST_IP = os.environ["EC2_HOST"]
REPO_NAME = os.environ["REPO_NAME"]
APP_PORT = os.environ["APP_PORT"]
IMAGE_TAG = os.environ["IMAGE_TAG"]

ecr_client = boto3.client("ecr")

auth = ecr_client.get_authorization_token()["authorizationData"][0]
username, password = base64.b64decode(auth["authorizationToken"]).decode().split(":")
registry = auth["proxyEndpoint"].replace("https://", "")


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=HOST_IP,
    username=SSH_USER,
    key_filename=SSH_KEY_FILE,
    timeout=10,
)

stdin, stdout, stderr = ssh.exec_command(f"docker login -u {username} --password-stdin {registry}")
stdin.write(password)
stdin.channel.shutdown_write()
if stdout.channel.recv_exit_status() != 0:
    print(f"docker login failed:\n{stderr.read().decode()}")
    sys.exit(1)
print("Logged in to ECR")

stdin, stdout, stderr = ssh.exec_command("docker rm -f nginx-app")
stdout.channel.recv_exit_status()

image = f"{registry}/{REPO_NAME}:{IMAGE_TAG}"
stdin, stdout, stderr = ssh.exec_command(f"docker run -d --name nginx-app -p {APP_PORT}:80 {image}")
if stdout.channel.recv_exit_status() != 0:
    print(f"docker run failed:\n{stderr.read().decode()}")
    sys.exit(1)
print(f"Container started from {image}")

ssh.close()