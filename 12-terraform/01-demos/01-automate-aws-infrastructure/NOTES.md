# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate AWS Infrastructure

### Demo Executed: Part 1 – VPC, subnet, routing and security group

#### Created VPC & Subnet
Created a new VPC and subnet with values from variables. The resources from the earlier demos were destroyed in the same apply.

`main.tf` and the apply:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    provider "aws" {
        region = "eu-central-1"
    }
    
    variable vpc_cidr_block {}
    variable subnet_cidr_block {}
    variable avail_zone {}
    variable env_prefix {}
    
    resource "aws_vpc" "myapp-vpc" {
        cidr_block = var.vpc_cidr_block
        tags = {
            Name: "${var.env_prefix}-vpc"
        }
    }
    
    resource "aws_subnet" "myapp-subnet-1" {
        vpc_id = aws_vpc.myapp-vpc.id
        cidr_block = var.subnet_cidr_block
        availability_zone = var.avail_zone
        tags = {
            Name: "${var.env_prefix}-subnet-1"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 2 to add, 0 to change, 2 to destroy.
    aws_subnet.dev-subnet-1: Destroying... [id=subnet-0ac4e9b5390417f7b]
    aws_vpc.myapp-vpc: Creating...
    aws_subnet.dev-subnet-1: Destruction complete after 1s
    aws_vpc.development-vpc: Destroying... [id=vpc-0e7925ca7de335498]
    aws_vpc.development-vpc: Destruction complete after 0s
    aws_vpc.myapp-vpc: Creation complete after 1s [id=vpc-01cb698649ba9cb82]
    aws_subnet.myapp-subnet-1: Creating...
    aws_subnet.myapp-subnet-1: Creation complete after 1s [id=subnet-0d0c73d53c8304752]
    
    Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```
<img width="1704" height="835" alt="image" src="https://github.com/user-attachments/assets/34e98593-d13c-4717-97f0-5cfa558504ae" />

<img width="1702" height="809" alt="image" src="https://github.com/user-attachments/assets/5e103ddf-82a3-4749-ad35-175f51f76661" />

#### Created custom Route Table
Created an Internet Gateway and a route table with a `0.0.0.0/0` route to it:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_route_table" "myapp-route-table" {
        vpc_id = aws_vpc.myapp-vpc.id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-rtb"
        }
    }
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = aws_vpc.myapp-vpc.id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 2 to add, 0 to change, 0 to destroy.
    aws_internet_gateway.myapp-igw: Creating...
    aws_internet_gateway.myapp-igw: Creation complete after 1s [id=igw-0cdf26ec1de16018d]
    aws_route_table.myapp-route-table: Creating...
    aws_route_table.myapp-route-table: Creation complete after 1s [id=rtb-0ecdf898f49754b61]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```
<img width="1710" height="833" alt="image" src="https://github.com/user-attachments/assets/379b2d17-18cd-4ca7-8d85-e17488fdc22a" />

#### Added Subnet Association with Route Table
Associated the subnet with the new route table using `aws_route_table_association`:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_route_table_association" "a-rtb-subnet" {
        subnet_id = aws_subnet.myapp-subnet-1.id
        route_table_id = aws_route_table.myapp-route-table.id
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_route_table_association.a-rtb-subnet: Creating...
    aws_route_table_association.a-rtb-subnet: Creation complete after 0s [id=rtbassoc-07c4ac24965795e66]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1694" height="825" alt="image" src="https://github.com/user-attachments/assets/5f640689-588d-4002-8acb-8b06a15fca59" />

#### Configured Default/Main Route Table
Then switched to the route table AWS creates with the VPC. Commented out the custom route table and the association, and added the IGW route to the main route table with `aws_default_route_table`:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    /* Custom Route Table commented out */
    
    resource "aws_default_route_table" "main-rtb" {
        default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-main-rtb"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_default_route_table.main-rtb: Creating...
    aws_default_route_table.main-rtb: Creation complete after 0s [id=rtb-002936ab76ff4961e]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1710" height="825" alt="image" src="https://github.com/user-attachments/assets/8e641332-408b-4a32-83cd-b26b83318f72" />

#### Created Security Group
Created a security group: SSH (22) only from my IP, 8080 open to everyone, all outbound traffic allowed:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_security_group" "myapp-sg" {
        name = "myapp-sg"
        vpc_id = aws_vpc.myapp-vpc.id
    
        ingress{
            from_port = 22
            to_port = 22
            protocol = "TCP"
            cidr_blocks = [var.my_ip]
        }
    
        ingress{
            from_port = 8080
            to_port = 8080
            protocol = "TCP"
            cidr_blocks = ["0.0.0.0/0"]
        }
    
        egress{
            from_port = 0
            to_port = 0
            protocol = "-1"
            cidr_blocks = ["0.0.0.0/0"]
            prefix_list_ids = []
        }
    
        tags = {
            Name: "${var.env_prefix}-sg"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_security_group.myapp-sg: Creating...
    aws_security_group.myapp-sg: Creation complete after 3s [id=sg-04a0b7384ea23fdfc]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1704" height="635" alt="image" src="https://github.com/user-attachments/assets/664faf91-0c84-4953-8f86-5ebf540fe328" />

#### Configured Default Security Group
Same idea as the route table: replaced the custom SG with `aws_default_security_group`, using the same rules.

<img width="1708" height="701" alt="image" src="https://github.com/user-attachments/assets/5e46d969-e203-46c8-a0b3-878d8277420d" />

The apply destroys the custom SG and takes over the default one:

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    aws_security_group.myapp-sg: Destroying... [id=sg-04a0b7384ea23fdfc]
    aws_default_security_group.default-sg: Creating...
    aws_security_group.myapp-sg: Destruction complete after 1s
    aws_default_security_group.default-sg: Creation complete after 2s [id=sg-0bc899b0d94188f99]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

### Demo Executed: Part 2 – EC2 instance and SSH key pair

#### Created EC2 Instance (Manual Key Pair Approach)
First created a `t2.micro` instance with a key pair I made in the AWS console (`server-key-pair.pem`). Restricted the key permissions, then applied:

```bash
    root@PC:~/modules/terraform (feature/EC2)# ls ~/.ssh/server-key-pair.pem
    /root/.ssh/server-key-pair.pem
    root@PC:~/modules/terraform (feature/EC2)# chmod 400 ~/.ssh/server-key-pair.pem
    root@PC:~/modules/terraform (feature/EC2)# ls -l ~/.ssh/server-key-pair.pem
    -r-------- 1 root root 1678 Sep  5 21:00 /root/.ssh/server-key-pair.pem

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Creation complete after 13s [id=i-06ca00864feabd5a8]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

#### SSH into EC2 Instance (Manual Key)
Connected to the new Amazon Linux 2023 server with the downloaded `.pem` key:

```bash
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/server-key-pair.pem ec2-user@18.192.8.225
    The authenticity of host '18.192.8.225 (18.192.8.225)' can't be established.
    ED25519 key fingerprint is SHA256:4jQZsvFbwQg80vSiK0YNniKkZj3t/In4CCjv2qZr1AI.
    This key is not known by any other names.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    Warning: Permanently added '18.192.8.225' (ED25519) to the list of known hosts.
    ...
    [ec2-user@ip-10-0-10-185 ~]$ exit
    logout
    Connection to 18.192.8.225 closed.
```

#### Configured SSH Key Pair in Terraform Config File
To skip the console step, added an `aws_key_pair` resource that uses my local public key (`id_rsa.pub`). The AMI comes from a `data "aws_ami"` block (latest Amazon Linux 2023):

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    
    data "aws_ami" "latest-amazon-linux-image" {
        most_recent = true
        owners = ["amazon"]
        filter {
            name = "name"
            values = ["al2023-ami-2023.*-x86_64"]
        }
        filter{
            name = "virtualization-type"
            values = ["hvm"]
        }
    }
    
    resource "aws_key_pair" "ssh-key" {
        key_name = "server-key"
        public_key = file(var.public_key_location)
    }
    
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
```

#### Created EC2 Instance (Automated Key Pair)
The new `key_name` forces replacement, so Terraform destroyed the instance and created a new one with the new key:

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server must be replaced
    -/+ resource "aws_instance" "myapp-server" {
    ...
          ~ key_name                             = "server-key-pair" -> "server-key" # forces replacement
    ...
      # aws_key_pair.ssh-key will be created
      + resource "aws_key_pair" "ssh-key" {
          + key_name        = "server-key"
          + public_key      = "ssh-rsa AAAAB3NzaC1yc...[TRUNCATED]...root@PC"
    ...
    Plan: 2 to add, 0 to change, 1 to destroy.
    aws_instance.myapp-server: Destroying... [id=i-06ca00864feabd5a8]
    aws_instance.myapp-server: Destruction complete after 20s
    aws_key_pair.ssh-key: Creating...
    aws_key_pair.ssh-key: Creation complete after 0s [id=server-key]
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Creation complete after 13s [id=i-03ad6fbe423be3bde]
    
    Apply complete! Resources: 2 added, 0 changed, 1 destroyed.
```

#### SSH into EC2 Instance (Automated Key)
Got the public IP (`35.157.195.225`) from `terraform state show`, then connected with `id_rsa`. It also works without `-i`, because `id_rsa` is the default key. After that I deleted the old `.pem` key.

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform state show aws_instance.myapp-server
    ...
    
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/id_rsa ec2-user@35.157.195.225
    ...
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@35.157.195.225
    ...
    Last login: Sat Sep  5 18:22:33 2026 from <my-ip>
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# rm ~/.ssh/server-key-pair.pem
```
<img width="1905" height="927" alt="image" src="https://github.com/user-attachments/assets/0db12caa-d5f5-477e-aaec-b77d1ef9698c" />
<img width="1909" height="404" alt="image" src="https://github.com/user-attachments/assets/70dd2aec-28e6-4274-a35b-bfe648b36bd6" />

### Demo Executed: Part 3 – Install Docker and run nginx with user data

#### Configured Terraform to install Docker and run nginx image
Added `user_data` to the instance: update the OS, install and start Docker, add `ec2-user` to the docker group and run nginx on port 8080. In the first SSH session `docker ps` got `permission denied`, because the group change only applies to a new session. After reconnecting, the nginx container was running.

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server must be replaced
    -/+ resource "aws_instance" "myapp-server" {
    ...
      + user_data                            = <<-EOT # forces replacement
            #!/bin/bash
            sudo yum update -y && sudo yum install docker -y
            sudo systemctl start docker
            sudo usermod -aG docker ec2-user
            docker run -d -p 8080:80 nginx
        EOT
    ...
      ~ user_data_replace_on_change          = false -> true
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    ...
    aws_instance.myapp-server: Creation complete after 13s [id=i-0839b33e99a21adc8]
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    ec2_public_ip = "18.198.22.100"

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@18.198.22.100
    ...
    [ec2-user@ip-10-0-10-74 ~]$ docker ps
    permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.44/containers/json": dial unix /var/run/docker.sock: connect: permission denied
    [ec2-user@ip-10-0-10-74 ~]$ exit
    logout
    Connection to 18.198.22.100 closed.

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@18.198.22.100
    ...
    [ec2-user@ip-10-0-10-74 ~]$ docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                   NAMES
    0fcfec58c119   nginx     "/docker-entrypoint.…"   58 seconds ago   Up 56 seconds   0.0.0.0:8080->80/tcp, :::8080->80/tcp   jovial_hopper
```

#### Extract shell commands to own shell script
Moved the user data commands into `entry-script.sh` and loaded it with `file()`. Applied again and checked the container on the new instance:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat entry-script.sh
    #!/bin/bash
    sudo yum update -y && sudo yum install docker -y
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
    docker run -d -p 8080:80 nginx

    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        user_data = file("entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    ...
    aws_instance.myapp-server: Creation complete after 12s [id=i-0c8ebfbd84376417c]
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    ec2_public_ip = "3.79.21.47"

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@3.79.21.47
    ...
    [ec2-user@ip-10-0-10-134 ~]$ exit
    logout
    Connection to 3.79.21.47 closed.

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@3.79.21.47
    ...
    [ec2-user@ip-10-0-10-134 ~]$ docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                   NAMES
    a25a61191afb   nginx     "/docker-entrypoint.…"   39 seconds ago   Up 37 seconds   0.0.0.0:8080->80/tcp, :::8080->80/tcp   pedantic_wiles
```

#### Accessed nginx through Browser
Opened the nginx page in the browser with the instance's public IP on port 8080:

<img width="1344" height="315" alt="image" src="https://github.com/user-attachments/assets/348edfb5-4007-419a-9f96-7bf693536620" />

### Demo Executed: Provisioners

#### Used “remote-exec” provisioner
Ran an inline command on the new instance with `remote-exec`. Provisioners only run when the resource is created, so I used `-replace` to recreate the instance. Terraform connected over SSH and the command created `newdir`, which I checked with a manual SSH session:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# terraform apply -replace="aws_instance.myapp-server"
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server will be replaced, as requested
    -/+ resource "aws_instance" "myapp-server" {
    ...
    aws_instance.myapp-server: Destroying... [id=i-0c8ebfbd84376417c]
    aws_instance.myapp-server: Destruction complete after 30s
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Provisioning with 'remote-exec'...
    aws_instance.myapp-server (remote-exec): Connecting to remote host via SSH...
    aws_instance.myapp-server (remote-exec):   Host: 18.199.152.174
    aws_instance.myapp-server (remote-exec):   User: ec2-user
    aws_instance.myapp-server (remote-exec):   Password: false
    aws_instance.myapp-server (remote-exec):   Private key: true
    ...
    aws_instance.myapp-server (remote-exec): Connected!
    aws_instance.myapp-server: Creation complete after 19s [id=i-0cd8a7993b65908ea]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    aws_ami_id = "ami-030f85e68f5db92a9"
    ec2_public_ip = "18.199.152.174"

    root@PC:~/modules/terraform (feature/provisioners)# ssh ec2-user@18.199.152.174
    ...
    [ec2-user@ip-10-0-10-131 ~]$ ls
    newdir
    [ec2-user@ip-10-0-10-131 ~]$ exit
    logout
    Connection to 18.199.152.174 closed.
```

#### Used “file” provisioner
The `file` provisioner copies `entry-script.sh` from my machine to the `ec2-user` home directory on the server, so no manual `scp` is needed. The `connection` block tells Terraform how to SSH in:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
    ...
        connection {
            type = "ssh"
            host = self.public_ip
            user = "ec2-user"
            private_key = file(var.private_key_location)
        }
    
        provisioner "file" {
            source = "entry-script.sh"
            destination = "/home/ec2-user/entry-script-on-ec2.sh"
        }
    ...
```

#### Used “local-exec” provisioner
`local-exec` runs on my machine, not on the server. Here it writes the instance's public IP to `output.txt`. `remote-exec` with `script` runs the uploaded script on the server:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
    ...
        provisioner "remote-exec" {
            script = "entry-script.sh"
        }
    
        provisioner "local-exec" {
            command = "echo ${self.public_ip} > output.txt"
        }
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
```
