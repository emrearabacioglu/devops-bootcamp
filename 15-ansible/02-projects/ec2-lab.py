#!/usr/bin/env python3
"""
EC2 tool for Ansible exercises.

python3 ec2-lab.py up                      # 1 Amazon Linux 2023 instance
python3 ec2-lab.py up --count 2 --os ubuntu
python3 ec2-lab.py up --ports 8080 3000    # also open these ports to everyone
python3 ec2-lab.py list
python3 ec2-lab.py down                    # delete everything the script created

`up` and `down` keep an Ansible inventory file (hosts.ini) in the current folder
up to date, so after `up` you can run: ansible all -i hosts.ini -m ping
"""

import argparse
import socket
import sys
import time
from pathlib import Path

import boto3
import requests
from botocore.exceptions import ClientError

# Config
LAB_TAG = "ansible-lab"
INSTANCE_TYPE = "t3.micro"
KEY_NAME = "ansible-lab"
SG_NAME = "ansible-lab-sg"
PUBLIC_KEY = Path.home() / ".ssh" / "id_rsa.pub"
PRIVATE_KEY = "~/.ssh/id_rsa"
INVENTORY = Path("hosts.ini")

OS_CONFIG = {
    "amazon": {
        "ami_param": "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64",
        "user": "ec2-user",
    },
    "ubuntu": {
        "ami_param": "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id",
        "user": "ubuntu",
    },
}

ec2 = boto3.client("ec2")
ssm = boto3.client("ssm")


# Helpers
def get_my_ip():
    return requests.get("https://checkip.amazonaws.com", timeout=5).text.strip()


def get_lab_instances(states=("pending", "running")):
    # Return the lab instances in the given states
    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Project", "Values": [LAB_TAG]},
            {"Name": "instance-state-name", "Values": list(states)},
        ]
    )
    return [i for r in response["Reservations"] for i in r["Instances"]]


def get_tag(instance, key):
    for tag in instance.get("Tags", []):
        if tag["Key"] == key:
            return tag["Value"]
    return ""


def wait_for_ssh(ip, retries=30, delay=5):
    # Wait until port 22 accepts connections
    for _ in range(retries):
        try:
            socket.create_connection((ip, 22), timeout=3).close()
            return True
        except OSError:
            time.sleep(delay)
    return False


# Setup
def ensure_key_pair():
    # Import ~/.ssh/id_rsa.pub as a key pair if it is not in AWS yet
    try:
        ec2.describe_key_pairs(KeyNames=[KEY_NAME])
    except ClientError:
        ec2.import_key_pair(KeyName=KEY_NAME, PublicKeyMaterial=PUBLIC_KEY.read_bytes())
        print(f"Key pair {KEY_NAME} imported from {PUBLIC_KEY}")


def get_security_group():
    # Return the lab security group ID, or None
    response = ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [SG_NAME]}]
    )
    groups = response["SecurityGroups"]
    return groups[0]["GroupId"] if groups else None


def ensure_security_group(extra_ports):
    # Create the lab security group if needed and open SSH (my IP) and extra ports (everyone)
    sg_id = get_security_group()
    if sg_id is None:
        vpc_id = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])[
            "Vpcs"
        ][0]["VpcId"]
        sg_id = ec2.create_security_group(
            GroupName=SG_NAME, Description="Ansible lab", VpcId=vpc_id
        )["GroupId"]
        print(f"Security group {SG_NAME} created")

    rules = [(22, f"{get_my_ip()}/32")] + [(port, "0.0.0.0/0") for port in extra_ports]
    for port, cidr in rules:
        try:
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": port,
                        "ToPort": port,
                        "IpRanges": [{"CidrIp": cidr}],
                    }
                ],
            )
            print(f"Port {port} opened for {cidr}")
        except ClientError as ex:
            if ex.response["Error"]["Code"] != "InvalidPermission.Duplicate":
                raise
    return sg_id


def write_inventory():
    # Write hosts.ini from all running lab instances, grouped by OS
    instances = get_lab_instances(states=("running",))
    if not instances:
        INVENTORY.unlink(missing_ok=True)
        return

    groups = {}
    for instance in instances:
        groups.setdefault(get_tag(instance, "OS"), []).append(instance["PublicIpAddress"])

    lines = []
    for os_name, ips in groups.items():
        lines.append(f"[{os_name}]")
        lines.extend(ips)
        lines.append("")
        lines.append(f"[{os_name}:vars]")
        lines.append(f"ansible_user={OS_CONFIG[os_name]['user']}")
        lines.append("")
    lines.append("[all:vars]")
    lines.append(f"ansible_ssh_private_key_file={PRIVATE_KEY}")
    lines.append("ansible_ssh_common_args='-o StrictHostKeyChecking=no'")

    INVENTORY.write_text("\n".join(lines) + "\n")
    print(f"Inventory written to {INVENTORY.resolve()}")


# Commands
def up(count, os_name, ports):
    ensure_key_pair()
    sg_id = ensure_security_group(ports)
    image_id = ssm.get_parameter(Name=OS_CONFIG[os_name]["ami_param"])["Parameter"]["Value"]

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[sg_id],
        MinCount=count,
        MaxCount=count,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": f"{LAB_TAG}-{os_name}"},
                    {"Key": "Project", "Value": LAB_TAG},
                    {"Key": "OS", "Value": os_name},
                ],
            }
        ],
    )
    ids = [i["InstanceId"] for i in response["Instances"]]
    print(f"Launched {', '.join(ids)}, waiting until running...")
    ec2.get_waiter("instance_running").wait(InstanceIds=ids)

    for instance in get_lab_instances(states=("running",)):
        if instance["InstanceId"] in ids:
            ip = instance["PublicIpAddress"]
            status = "SSH ready" if wait_for_ssh(ip) else "SSH not reachable yet"
            print(f"  {instance['InstanceId']}  {ip}  {status}")

    write_inventory()
    print("Test with: ansible all -i hosts.ini -m ping")


def list_instances():
    instances = get_lab_instances(states=("pending", "running", "stopping", "stopped"))
    if not instances:
        print("No lab instances")
        return
    for instance in instances:
        print(
            f"{instance['InstanceId']}  {get_tag(instance, 'OS'):7}  "
            f"{instance.get('PublicIpAddress', '-'):15}  {instance['State']['Name']}"
        )


def down():
    instances = get_lab_instances(states=("pending", "running", "stopping", "stopped"))
    ids = [i["InstanceId"] for i in instances]
    if ids:
        ec2.terminate_instances(InstanceIds=ids)
        print(f"Terminating {', '.join(ids)}, waiting...")
        ec2.get_waiter("instance_terminated").wait(InstanceIds=ids)

    sg_id = get_security_group()
    if sg_id:
        # The network interfaces can take a few seconds to detach after termination
        for _ in range(10):
            try:
                ec2.delete_security_group(GroupId=sg_id)
                print(f"Security group {SG_NAME} deleted")
                break
            except ClientError:
                time.sleep(5)
        else:
            print(f"Could not delete {SG_NAME}, delete it from the console")

    try:
        ec2.delete_key_pair(KeyName=KEY_NAME)
        print(f"Key pair {KEY_NAME} deleted")
    except ClientError:
        pass

    INVENTORY.unlink(missing_ok=True)
    print("Lab is clean")


def main():
    parser = argparse.ArgumentParser(description="Quick EC2 lab for Ansible exercises")
    sub = parser.add_subparsers(dest="command", required=True)

    up_parser = sub.add_parser("up", help="create instances")
    up_parser.add_argument("--count", type=int, default=1)
    up_parser.add_argument("--os", choices=OS_CONFIG.keys(), default="amazon")
    up_parser.add_argument("--ports", type=int, nargs="*", default=[], help="extra ports open to everyone")

    sub.add_parser("list", help="show lab instances")
    sub.add_parser("down", help="delete instances, security group and key pair")

    args = parser.parse_args()
    if args.command == "up":
        up(args.count, args.os, args.ports)
    elif args.command == "list":
        list_instances()
    else:
        down()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Stopped")