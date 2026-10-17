"""
EXERCISE 3: Automate Running and Monitoring Application on EC2 instance

- Start EC2 instance in default VPC (reuse it if it already exists)
- Wait until the EC2 server is fully initialized
- Open ports for SSH (own IP only) and nginx (public)
- Install Docker on the EC2 server and start nginx container
- Monitor the app on a schedule; restart nginx if it fails 5 times in a row
"""

import logging
import sys
import time

import boto3
import paramiko
import requests
import schedule

# Config
TAG_KEY = "Name"
TAG_VALUE = "boto3-server"
INSTANCE_TYPE = "t3.micro"
AMI_NAME_PATTERN = "al2023-ami-2023.*-x86_64"
KEY_NAME = "my-key"

SSH_KEY_PATH = "/root/.ssh/id_rsa"
SSH_USER = "ec2-user"

APP_PORT = 8080
CHECK_INTERVAL_SECONDS = 5
FAIL_THRESHOLD = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

ec2_client = boto3.client("ec2")
fail_count = 0


# EC2
def find_existing_instance():
    # Return the ID of a existing instance with our tag, or None
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]},
        ]
    )
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance["InstanceId"]
    return None


def get_latest_ami():
    # Return the ID of the newest Amazon Linux 2023 AMI
    images = ec2_client.describe_images(
        Owners=["amazon"],
        Filters=[{"Name": "name", "Values": [AMI_NAME_PATTERN]}],
    )["Images"]
    latest = sorted(images, key=lambda i: i["CreationDate"], reverse=True)[0]
    return latest["ImageId"]


def create_instance(image_id):
    # Launch a new tagged instance and return its ID
    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": TAG_KEY, "Value": TAG_VALUE}],
            }
        ],
    )
    return response["Instances"][0]["InstanceId"]


def wait_until_ready(instance_id):
    # Block until both instance and system status checks are ok
    ec2_client.get_waiter("instance_status_ok").wait(InstanceIds=[instance_id])
    ec2_client.get_waiter("system_status_ok").wait(InstanceIds=[instance_id])


def get_instance_info(instance_id):
    # Return the public IP and security group ID of the instance
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response["Reservations"][0]["Instances"][0]
    return instance["PublicIpAddress"], instance["SecurityGroups"][0]["GroupId"]


# Security group
def get_my_ip():
    # Return the public IP of the machine running this script
    return requests.get("https://checkip.amazonaws.com", timeout=5).text.strip()


def build_rules(my_ip):
    # Return the ingress rules: nginx open to everyone, SSH only to my IP
    return [
        {
            "IpProtocol": "tcp",
            "FromPort": APP_PORT,
            "ToPort": APP_PORT,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": f"{my_ip}/32"}],
        },
    ]


def rule_exists(permissions, port, cidr):
    # Check if a rule for this port and CIDR is already in the security group
    for perm in permissions:
        if perm.get("FromPort") == port:
            for ip_range in perm["IpRanges"]:
                if ip_range["CidrIp"] == cidr:
                    return True
    return False


def open_ports(sg_id, rules):
    # Add the rules that are not already in the security group
    permissions = ec2_client.describe_security_groups(GroupIds=[sg_id])[
        "SecurityGroups"
    ][0]["IpPermissions"]

    for rule in rules:
        port = rule["FromPort"]
        cidr = rule["IpRanges"][0]["CidrIp"]
        if rule_exists(permissions, port, cidr):
            log.info(f"Port {port} already open for {cidr}")
        else:
            ec2_client.authorize_security_group_ingress(
                GroupId=sg_id, IpPermissions=[rule]
            )
            log.info(f"Port {port} opened for {cidr}")


# SSH
def connect_ssh(host_ip, retries=5, delay=10):
    # Return a connected SSH client, or None if all attempts fail
    for attempt in range(1, retries + 1):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=host_ip,
                username=SSH_USER,
                key_filename=SSH_KEY_PATH,
                timeout=10,
            )
            return ssh
        except Exception as ex:
            log.warning(f"SSH attempt {attempt}/{retries} failed: {ex}")
            time.sleep(delay)
    return None


def run_cmd(ssh, cmd, retries=3, delay=10):
    # Run a command over SSH with retries. Return True on success
    for attempt in range(1, retries + 1):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if stdout.channel.recv_exit_status() == 0:
            return True
        log.warning(
            f"Attempt {attempt}/{retries} failed for '{cmd}':\n{stderr.read().decode()}"
        )
        time.sleep(delay)
    return False


def setup_app(ssh):
    # Install Docker and start the nginx container. Return True on success
    commands = [
        "sudo dnf update -y && sudo dnf install -y docker && sudo systemctl start docker",
        f"sudo docker start nginx 2>/dev/null || sudo docker run -d -p {APP_PORT}:80 --name nginx nginx",
    ]
    for cmd in commands:
        if not run_cmd(ssh, cmd):
            return False
    return True


# Monitoring
def restart_container(host_ip):
    # Restart the nginx container over SSH
    log.info("Restarting nginx container...")
    ssh = connect_ssh(host_ip)
    if ssh is None:
        log.error("Restart failed: could not connect via SSH")
        return
    if run_cmd(ssh, "sudo docker restart nginx"):
        log.info("nginx restarted")
    else:
        log.error("nginx restart failed")
    ssh.close()


def monitor_application(host_ip):
    # Check the app once; restart nginx after FAIL_THRESHOLD failures in a row
    global fail_count
    try:
        response = requests.get(f"http://{host_ip}:{APP_PORT}/", timeout=5)
        if response.status_code == 200:
            log.info("All good! (200)")
            fail_count = 0
            return
        log.warning(f"App returned status {response.status_code}")
    except requests.RequestException as ex:
        log.warning(f"Connection error: {ex}")

    fail_count += 1
    log.warning(f"Failed {fail_count} time(s) in a row")
    if fail_count >= FAIL_THRESHOLD:
        restart_container(host_ip)
        fail_count = 0


def start_monitoring(host_ip):
    # Run monitor_application every CHECK_INTERVAL_SECONDS, forever
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(monitor_application, host_ip)
    log.info(
        f"Monitoring http://{host_ip}:{APP_PORT} every {CHECK_INTERVAL_SECONDS} sec"
    )
    while True:
        schedule.run_pending()
        time.sleep(1)


# Main
def abort(instance_id, created):
    # Stop the script; terminate the instance only if it was created in this run
    if created:
        log.error(f"Setup failed, terminating instance {instance_id}")
        ec2_client.terminate_instances(InstanceIds=[instance_id])
    else:
        log.error(f"Setup failed, existing instance {instance_id} left running")
    sys.exit(1)


def main():
    instance_id = find_existing_instance()
    created = instance_id is None
    if created:
        instance_id = create_instance(get_latest_ami())
        log.info(f"Instance {instance_id} created")
    else:
        log.info(f"Instance {instance_id} already exists, reusing it")

    log.info("Waiting for instance and system status checks...")
    wait_until_ready(instance_id)
    log.info("Instance is ready")

    host_ip, sg_id = get_instance_info(instance_id)
    open_ports(sg_id, build_rules(get_my_ip()))

    log.info("Installing Docker and starting nginx...")
    ssh = connect_ssh(host_ip)
    if ssh is None or not setup_app(ssh):
        abort(instance_id, created)
    ssh.close()
    log.info(f"nginx is running at http://{host_ip}:{APP_PORT}")

    start_monitoring(host_ip)


def print_cleanup_commands():
    # Print the AWS CLI commands to clean up the instance and SG rules
    instance_id = find_existing_instance()
    if instance_id is None:
        log.info("No running instance found, nothing to clean up")
        return
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    sg_id = response["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]
    my_ip = get_my_ip()
    print(f"""
        To clean up, run:
        
        aws ec2 terminate-instances --instance-ids {instance_id}
        aws ec2 revoke-security-group-ingress --group-id {sg_id} --protocol tcp --port {APP_PORT} --cidr 0.0.0.0/0
        aws ec2 revoke-security-group-ingress --group-id {sg_id} --protocol tcp --port 22 --cidr {my_ip}/32
        """)


if __name__ == "__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        log.info("Stopped by user")
        print_cleanup_commands()
