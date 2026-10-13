# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Interacting with AWS CLI

### Demo Executed: EC2 and IAM resources with the AWS CLI

#### Overview
Did everything from the CLI instead of the console. First part: security group, key pair and EC2 instance. Second part: filtering EC2 output, creating an IAM group, user and policies, then testing the new user's permissions with its own access keys.

#### Part 1: EC2

##### CLI Configuration
Checked the configured credentials and region:

    root@PC:/mnt/c/Users/emrea# aws configure
    AWS Access Key ID [****************QHCO]: ****************QHCO
    AWS Secret Access Key [****************b8EN]: ****************b8EN
    Default region name [eu-central-1]: eu-central-1

##### VPC and Subnet IDs
Got the default VPC and a subnet ID to use for the instance:

    root@PC:/mnt/c/Users/emrea# aws ec2 describe-vpcs
    {
        "Vpcs": [
            {
                "VpcId": "vpc-0a332f5fe30a6dad5",
                "CidrBlock": "172.31.0.0/16",
                "IsDefault": true
                ...
            }
        ]
    }

    root@PC:/mnt/c/Users/emrea# aws ec2 describe-subnets
    {
        "Subnets": [
            {
                "SubnetId": "subnet-0e7c3045a7bed0241",
                "VpcId": "vpc-0a332f5fe30a6dad5",
                "AvailabilityZone": "eu-central-1c"
                ...
            }
        ]
    }

##### Security Group
Created `my-sg` and allowed SSH only from my IP:

    root@PC:/mnt/c/Users/emrea# aws ec2 create-security-group --group-name my-sg --description "my SG" --vpc-id vpc-0a332f5fe30a6dad5
    {
        "GroupId": "sg-0d8d98c7c091aa89d",
        ...
    }

    root@PC:/mnt/c/Users/emrea# aws ec2 authorize-security-group-ingress \
    > --group-id sg-0d8d98c7c091aa89d \
    > --protocol tcp \
    > --port 22 \
    > --cidr <my-ip>/32

    root@PC:/mnt/c/Users/emrea# aws ec2 describe-security-groups --group-ids sg-0d8d98c7c091aa89d
    ...
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "<my-ip>/32"}]
    ...

<img width="1901" height="530" alt="image" src="https://github.com/user-attachments/assets/38de84ed-9602-4861-988f-227e8e9844d9" />

##### Key Pair
Created a key pair and saved the private key to a file:

    root@PC:/mnt/c/Users/emrea# aws ec2 create-key-pair \
    > --key-name MyKpCli \
    > --query 'KeyMaterial' \
    > --output text > MyKpCli.pem

##### EC2 Instance
Started a `t2.micro` instance with the new SG, key and subnet:

    root@PC:/mnt/c/Users/emrea# aws ec2 run-instances \
    > --image-id ami-036bdae36143a955f \
    > --count 1 \
    > --instance-type t2.micro \
    > --key-name MyKpCli \
    > --security-group-ids sg-0d8d98c7c091aa89d \
    > --subnet-id subnet-0e7c3045a7bed0241

    root@PC:/mnt/c/Users/emrea# aws ec2 describe-instances
    ...
                "InstanceId": "i-077580233aa60e75c",
                "State": {"Code": 16, "Name": "running"},
                "PublicIpAddress": "35.159.167.194",
                "KeyName": "MyKpCli",
    ...

<img width="1919" height="864" alt="image" src="https://github.com/user-attachments/assets/8046546b-abc5-455e-81f7-3531c1f048f5" />

##### SSH Access
`chmod` doesn't work on the Windows filesystem in WSL, so I copied the key to `~/.ssh` first:

    root@PC:~/.ssh# cp /mnt/c/Users/emrea/MyKpCli.pem ~/.ssh/
    root@PC:~# chmod 400 ~/.ssh/MyKpCli.pem
    root@PC:~# ssh -i .ssh/MyKpCli.pem ec2-user@35.159.167.194
    ...
    [ec2-user@ip-172-31-14-74 ~]$

#### Part 2: Filtering and IAM

##### Filter and Query
Got only the instance IDs of instances with a specific tag:

    root@PC:~/.ssh# aws ec2 describe-instances --filters "Name=tag:Type,Values=web-server-with-docker" --query "Reservations[].Instances[].InstanceId"
    [
        "i-04035f9eae72a81c2"
    ]

##### Group and User
Created a group and a user, then added the user to the group:

    root@PC:~/.ssh# aws iam create-group --group-name MyGroupCli
    {
        "Group": {
            "GroupName": "MyGroupCli",
            "Arn": "arn:aws:iam::731872836472:group/MyGroupCli",
            ...
        }
    }

    root@PC:~/.ssh# aws iam create-user --user-name MyUserCli
    {
        "User": {
            "UserName": "MyUserCli",
            "Arn": "arn:aws:iam::731872836472:user/MyUserCli",
            ...
        }
    }

    root@PC:~/.ssh# aws iam add-user-to-group --user-name MyUserCli --group-name MyGroupCli
    root@PC:~/.ssh# aws iam get-group --group-name MyGroupCli
    {
        "Users": [
            {
                "UserName": "MyUserCli",
                ...
            }
        ],
        "Group": {
            "GroupName": "MyGroupCli",
            ...
        }
    }

<img width="1648" height="211" alt="image" src="https://github.com/user-attachments/assets/8db2a7f5-d5af-4c1c-a817-e07e51167ac9" />
<img width="1629" height="406" alt="image" src="https://github.com/user-attachments/assets/f38b6ae1-ebdd-4a0c-9ff8-a3dbc85a8a65" />
<img width="1900" height="581" alt="image" src="https://github.com/user-attachments/assets/a79d7320-c9ed-4264-a874-0faf9a22efd3" />

##### Group Policy
Attached the AWS-managed `AmazonEC2FullAccess` policy to the group:

    root@PC:~/.ssh# aws iam attach-group-policy --group-name MyGroupCli --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

    root@PC:~/.ssh# aws iam list-attached-group-policies --group-name MyGroupCli
    {
        "AttachedPolicies": [
            {
                "PolicyName": "AmazonEC2FullAccess",
                "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
            }
        ]
    }

##### Console Password
Gave the user a console password:

    root@PC:~/.ssh# aws iam create-login-profile --user-name MyUSerCli --password ***
    {
        "LoginProfile": {
            "UserName": "MyUserCli",
            "PasswordResetRequired": false
            ...
        }
    }

##### Custom Policy
Created a policy from `changePwdPolicy.json` that lets users change their own password, and attached it to the group:

    root@PC:~# aws iam create-policy --policy-name changePwd --policy-document file://changePwdPolicy.json
    {
        "Policy": {
            "PolicyName": "changePwd",
            "Arn": "arn:aws:iam::731872836472:policy/changePwd",
            ...
        }
    }
    root@PC:~# aws iam attach-group-policy --group-name MyGroupCli --policy-arn arn:aws:iam::731872836472:policy/changePwd

<img width="1621" height="605" alt="image" src="https://github.com/user-attachments/assets/53bef617-72a4-419a-be9e-431661a57a4b" />

##### Access Keys and Permission Test
Created access keys for the new user:

    root@PC:~# aws iam create-access-key --user-name MyUserCli
    {
        "AccessKey": {
            "UserName": "MyUserCli",
            "AccessKeyId": "**********",
            "Status": "Active",
            "SecretAccessKey": "**********",
            ...
        }
    }

Switched to the new user with environment variables. EC2 access works, IAM actions are denied:

    root@PC:~# export AWS_ACCESS_KEY_ID=**********
    root@PC:~# export AWS_SECRET_ACCESS_KEY=**********

    root@PC:~# aws ec2 describe-instances
    {
        "Reservations": [
            {
                "ReservationId": "r-0e3f7abe0d6c32567",
                ...

    root@PC:~# aws iam create-user --user-name test
    aws: [ERROR]: An error occurred (AccessDenied) when calling the CreateUser operation: User: arn:aws:iam::731872836472:user/MyUserCli is not authorized to perform: iam:CreateUser ...

<img width="1898" height="896" alt="image" src="https://github.com/user-attachments/assets/c7cea04c-bf07-4c12-807a-4bc4609e43b9" />
