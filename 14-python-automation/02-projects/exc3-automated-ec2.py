# EXERCISE 3: Automate Running and Monitoring Application on EC2 instance
# Write a Python program which automatically creates an EC2 instance, installs Docker inside and starts an Nginx application as Docker container and starts monitoring the application as a scheduled task. Write the program with the following steps:

# Start EC2 instance in default VPC
# Wait until the EC2 server is fully initialized
# Install Docker on the EC2 server
# Start nginx container
# Open port for nginx to be accessible from browser
# Create a scheduled function that sends a request to the nginx application and checks the status is OK
# If status is not OK 5 times in a row, it restarts the nginx application

import boto3 
import schedule
import time
import paramiko
import sys
import requests

ec2_client = boto3.client("ec2")

print(f"############################### Starting EC2 Instance ###############################\n")

images = ec2_client.describe_images(
    Owners=["amazon"],
    Filters=[{"Name": "name", "Values": ["al2023-ami-2023.*-x86_64"]}],
)["Images"]
latest = sorted(images, key=lambda i: i["CreationDate"], reverse=True)[0]
image_id = latest["ImageId"]

instance = ec2_client.run_instances(
    InstanceType="t3.micro",
    ImageId=image_id,
    MinCount=1,
    MaxCount=1,
    KeyName= 'my-key',
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags':[
                {
                    'Key': 'Name',
                    'Value':'boto3server'
                },
            ]
        }
    ],
)
instance_id = instance["Instances"][0]["InstanceId"]

def check_instance_status():
    statuses = ec2_client.describe_instance_status(
        InstanceIds=[instance_id],
        IncludeAllInstances=True
    )
    for status in statuses['InstanceStatuses']:
        state = status['InstanceState']['Name']
        instance_ok = status["InstanceStatus"]["Status"]
        system_ok = status["SystemStatus"]["Status"]
        print(f"Instance {status['InstanceId']} is {state}.")
        
        if state == "running" and instance_ok == "ok" and system_ok == "ok":
            return schedule.CancelJob
    print("\n")

schedule.every(5).seconds.do(check_instance_status)

while True:
    schedule.run_pending()
    if not schedule.jobs:
        break
    time.sleep(1)


print(f"############################### Install Docker/ Start nginx ###############################\n")

response = ec2_client.describe_instances(InstanceIds=[instance_id])
public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
sg_id = response["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]


ec2_client.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "176.220.203.48/32"}],
        }
    ],
)


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
ssh.connect(hostname=public_ip, username='ec2-user', key_filename='/root/.ssh/id_rsa')


def run_cmd(cmd, retries=3):
    for attempt in range(1, retries + 1):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if stdout.channel.recv_exit_status() == 0:
            return
        print(f"Attempt {attempt} failed:\n{stderr.read().decode()}")
        time.sleep(10)

    print("All attempts failed, terminating instance")
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    sys.exit(1)

run_cmd("sudo dnf update -y && sudo dnf install -y docker && sudo systemctl start docker")
run_cmd("sudo docker run -d -p 8080:80 --name nginx nginx")

ssh.close()


def restart_container():
    print("Restarting the app...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(hostname=public_ip, username='ec2-user', key_filename='/root/.ssh/id_rsa')
    stdin, stdout, stderr = ssh.exec_command('sudo docker restart nginx')
    print(stdout.readlines())
    ssh.close()
    print('App restarted')
    
    
fail_count = 0

def monitor_application():
    global fail_count
    try:
        response = requests.get(f"http://{public_ip}:8080/", timeout=5)
        if response.status_code == 200:
            print("All good!")
            fail_count = 0
            return
        print(f"Status {response.status_code}")
    except Exception as ex:
        print(f"connection error.. {ex}")

    fail_count += 1
    print(f"Failed {fail_count} time(s) in a row")
    if fail_count >= 5:
        restart_container()
        fail_count = 0


schedule.every(5).seconds.do(monitor_application)

while True:
    schedule.run_pending()
    time.sleep(1)
    