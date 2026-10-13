# Interacting with AWS CLI

**Technologies:** AWS, Linux

I used the AWS CLI instead of the console to create an EC2 instance with its security group and key pair, and to create IAM resources (group, user, policies).

## Summary
1. Configured the AWS CLI with my access keys and region `eu-central-1`.
2. Got the default VPC and subnet IDs, created the security group `my-sg` and allowed SSH (port 22) only from my IP.
3. Created the key pair `MyKpCli`, started a `t2.micro` instance with it and connected with SSH.
4. Used `--filters` and `--query` to list only the IDs of instances with a specific tag.
5. Created the IAM group `MyGroupCli` and user `MyUserCli`, added the user to the group and attached `AmazonEC2FullAccess` to the group.
6. Gave the user a console password and created my own policy from `changePwdPolicy.json`, so users can change their own password. Attached it to the group.
7. Created access keys for the new user and tested them with environment variables: EC2 access works, IAM actions are denied.

## Run
```bash
aws configure

# EC2
aws ec2 describe-vpcs
aws ec2 describe-subnets
aws ec2 create-security-group --group-name my-sg --description "my SG" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <sg-id> --protocol tcp --port 22 --cidr <my-ip>/32
aws ec2 create-key-pair --key-name MyKpCli --query 'KeyMaterial' --output text > MyKpCli.pem
aws ec2 run-instances --image-id ami-036bdae36143a955f --count 1 --instance-type t2.micro \
    --key-name MyKpCli --security-group-ids <sg-id> --subnet-id <subnet-id>
aws ec2 describe-instances --filters "Name=tag:Type,Values=web-server-with-docker" --query "Reservations[].Instances[].InstanceId"

# IAM
aws iam create-group --group-name MyGroupCli
aws iam create-user --user-name MyUserCli
aws iam add-user-to-group --user-name MyUserCli --group-name MyGroupCli
aws iam attach-group-policy --group-name MyGroupCli --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam create-login-profile --user-name MyUserCli --password '***'
aws iam create-policy --policy-name changePwd --policy-document file://changePwdPolicy.json
aws iam attach-group-policy --group-name MyGroupCli --policy-arn arn:aws:iam::731872836472:policy/changePwd
aws iam create-access-key --user-name MyUserCli
```

## Result
The instance created from the CLI is running, and the new user can use EC2 but not IAM:
```
root@PC:/mnt/c/Users/emrea# aws ec2 describe-instances
...
            "InstanceId": "i-077580233aa60e75c",
            "State": {"Code": 16, "Name": "running"},
            "PublicIpAddress": "35.159.167.194",
            "KeyName": "MyKpCli",
...
root@PC:~# aws iam create-user --user-name test
aws: [ERROR]: An error occurred (AccessDenied) when calling the CreateUser operation: User: arn:aws:iam::731872836472:user/MyUserCli is not authorized to perform: iam:CreateUser ...
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
