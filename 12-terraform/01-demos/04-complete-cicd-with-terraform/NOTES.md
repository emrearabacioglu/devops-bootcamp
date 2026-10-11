# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Complete CI/CD with Terraform

### Demo Executed: Jenkins pipeline that provisions the server with Terraform and deploys to it

#### Created SSH key pair for EC2 Instance
Created the `myapp-key-pair` key pair in AWS. Jenkins uses it to SSH into the new server.

<img width="1900" height="393" alt="image" src="https://github.com/user-attachments/assets/39bcd1a4-63ea-43cc-b4e9-7d01332bcfa8" />

#### Created Credential in Jenkins
Added the credentials the pipeline needs in Jenkins: AWS access keys for Terraform, Docker Hub login, and the EC2 SSH private key.

#### Installed Terraform inside Jenkins Container
Installed Terraform inside the Jenkins Docker container so the pipeline can run `terraform` commands.

#### Created Terraform configuration files to provision an ec2 server
The config creates a VPC, subnet, internet gateway, route table, security group and a `t2.micro` instance with the latest Amazon Linux 2023 AMI and `entry-script.sh` as user data. SSH is allowed from my IP and the Jenkins server IP.

`variables.tf` and `main.tf`:

    root@PC:~/modules/terraform/java-terraform# cat variables.tf
    variable vpc_cidr_block {
        default = "10.0.0.0/16"
    }
    variable subnet_cidr_block {
        default = "10.0.10.0/24"
    }
    variable avail_zone {
        default = "eu-central-1a"
    }
    variable env_prefix {
        default = "dev"
    }
    variable my_ip{
        default = "<my-ip>/32"
    }
    variable jenkins_ip {
        default = "142.93.104.61/32"
    }
    variable instance_type{
        default = "t2.micro"
    }
    variable region {
        default = "eu-central-1"
    }

    root@PC:~/modules/terraform/java-terraform# cat main.tf
    provider "aws" {
        region = var.region
    }
    
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
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = aws_vpc.myapp-vpc.id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }
    
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
    
    resource "aws_default_security_group" "default-sg" {
        vpc_id = aws_vpc.myapp-vpc.id
    
        ingress{
            from_port = 22
            to_port = 22
            protocol = "TCP"
            cidr_blocks = [var.my_ip, var.jenkins_ip]
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
            Name: "${var.env_prefix}-default-sg"
        }
    }
    
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
    
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = "myapp-key-pair"
    
        user_data = file("entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
    
    output "ec2_public_ip" {
        value = aws_instance.myapp-server.public_ip
    }

#### Created entry-script.sh and server-cmds.sh
`entry-script.sh` installs Docker and Docker Compose when the server starts. `server-cmds.sh` runs on the server during deploy: it logs in to Docker Hub and starts the containers with Docker Compose.

`server-cmds.sh`:

    root@PC:~/modules/terraform/java-terraform# cat server-cmds.sh
    #!/usr/bin/env bash
    
    export IMAGE=$1
    export DOCKER_USER=$2
    export DOCKER_PWD=$3
    
    echo $DOCKER_PWD | docker login -u $DOCKER_USER --password-stdin
    docker-compose -f docker-compose.yaml up --detach
    echo "success"

#### Adjusted Jenkinsfile to include provision and deployment stages (with Docker Login)
The pipeline builds the jar, builds and pushes the image, runs Terraform in the `provision server` stage, and deploys over SSH. The EC2 IP comes from `terraform output -raw ec2_public_ip`, and the deploy stage waits 90 seconds for the server to finish starting up.

`Jenkinsfile`:

    root@PC:~/modules/terraform/java-terraform# cat Jenkinsfile
    #!/usr/bin/env groovy
    
    library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
        [$class: 'GitSCMSource',
         remote: 'https://github.com/emrearabacioglu/jenkins-shared-library.git',
         credentialsId: 'github-credentials'
        ]
    )
    pipeline {
        agent any
        
        tools {
            maven 'maven-3.9'
        }
        environment {
            IMAGE_NAME = "emrearabacioglu/demo-app:1.1.12-4"
        }
        stages {
            stage('build app') {
                steps {
                    script {
                        echo 'building application jar...'
                        buildJar()
                    }
                }
            }
            stage('build image') {
                steps {
                    script {
                        echo 'building the docker image...'
                        buildImage(env.IMAGE_NAME)
                        dockerLogin()
                        dockerPush(env.IMAGE_NAME)
                    }
                }
            } 
            stage("provision server" ) {
                environment {
                    AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                    AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_access_secret_key')
                    TF_VAR_env_prefix = 'test'
                }
              steps {
                script {
                    dir ('terraform') {
                        sh "terraform init"
                        sh "terraform apply --auto-approve"
                        env.EC2_PUBLIC_IP = sh (
                            script: "terraform output -raw ec2_public_ip",
                            returnStdout: true
                        ).trim()
                    }
                }
              }
            }
            stage('deploy') {
                environment {
                    DOCKER_CREDS = credentials('docker-hub-repo')
                }
                steps {
                    script {
                        echo"waiting initialization"
                        sleep(time: 90, unit: "SECONDS")
    
                        echo 'deploying docker image to EC2...'
                        echo "${EC2_PUBLIC_IP}"
    
                        def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME} ${DOCKER_CREDS_USR} ${DOCKER_CREDS_PSW}"
                        def ec2Instance = "ec2-user@${EC2_PUBLIC_IP}"
    
                        sshagent(['server-ssh-key']) {
                            sh "scp -o StrictHostKeyChecking=no server-cmds.sh ${ec2Instance}:/home/ec2-user"
                            sh "scp -o StrictHostKeyChecking=no docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                            sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                        }
                    }
                }               
            }
        }
    }

#### Pipeline Run
All stages passed: jar built, image pushed to Docker Hub, Terraform had no changes to make (the server already existed), and the containers were started on EC2.

Pipeline log:

    Started by user emre
    ...
    [Pipeline] { (build app)
    ...
    [INFO] BUILD SUCCESS
    ...
    [Pipeline] { (build image)
    ...
    + docker build -t emrearabacioglu/demo-app:1.1.12-4 .
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    + docker push emrearabacioglu/demo-app:1.1.12-4
    ...
    1.1.12-4: digest: sha256:378325c256fab6f2f5b6613244c89d22e0ecd65eb7aef03ff738845e603964a5 size: 1159
    ...
    [Pipeline] { (provision server)
    ...
    + terraform apply --auto-approve
    No changes. Your infrastructure matches the configuration.
    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
    Outputs:
    ec2_public_ip = "3.75.191.235"
    ...
    [Pipeline] { (deploy)
    ...
    + scp -o StrictHostKeyChecking=no server-cmds.sh ec2-user@3.75.191.235:/home/ec2-user
    + scp -o StrictHostKeyChecking=no docker-compose.yaml ec2-user@3.75.191.235:/home/ec2-user
    + ssh -o StrictHostKeyChecking=no ec2-user@3.75.191.235 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.12-4 emrearabacioglu ****
    Login Succeeded
    ...
    Image emrearabacioglu/demo-app:1.1.12-4 Pulled
    Container ec2-user-postgres-1 Started
    success
    ...
    Finished: SUCCESS

<img width="1881" height="516" alt="image" src="https://github.com/user-attachments/assets/a91d42a1-bb18-4ccb-8892-5315caa8faf0" />

<img width="1907" height="931" alt="image" src="https://github.com/user-attachments/assets/21635cc0-bee7-489a-bcdb-891fdf1ec03b" />

#### Check on the Server
Connected to the instance and listed the running containers:

    root@PC:~/.ssh# ssh -i myapp-key-pair.pem ec2-user@3.75.191.235
    ...
    [ec2-user@ip-10-0-10-92 ~]$ docker ps
    CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                                       NAMES
    a008008b9c2b   postgres:16   "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
    f61c820ffc2e   nginx         "/docker-entrypoint.…"   9 minutes ago   Up 9 minutes   0.0.0.0:8080->80/tcp, :::8080->80/tcp       elated_chaplygin

## Configure a Shared Remote State

### Demo Executed: Store the Terraform state in S3

#### Infrastructure Teardown & Preparation
Before switching to remote state, destroyed the existing infrastructure manually from inside the Jenkins container, so the old local state would not conflict with the new backend.

#### AWS S3 Bucket Creation
Created an S3 bucket for the state file. This way Jenkins and my local machine use the same state.

#### Terraform Configuration Update
Added an `s3` backend to the `terraform` block in `main.tf`, so the state goes to the bucket instead of the Jenkins workspace:

    terraform {
      required_version = ">= 0.12"
      backend "s3" {
        bucket = "myapp-tf-s3-bucket-3673"
        key = "myapp/state.tfstate"
        region = "eu-central-1"
      }
    }

#### Executed CI/CD Pipeline with Remote Backend
Ran the pipeline again. `terraform init` configured the S3 backend, the apply created the server, and the app was deployed:

    Running in /var/jenkins_home/workspace/java-terraform_master/terraform
    ...
    + terraform init
    Initializing the backend...
    
    Successfully configured the backend "s3"! Terraform will automatically
    use this backend unless the backend configuration changes.
    
    Initializing provider plugins...
    - Reusing previous version of hashicorp/aws from the dependency lock file
    - Using previously-installed hashicorp/aws v6.63.0
    
    Terraform has been successfully initialized!
    ...
    + terraform apply --auto-approve
    data.aws_ami.latest-amazon-linux-image: Reading...
    data.aws_ami.latest-amazon-linux-image: Read complete after 0s [id=ami-030f85e68f5db92a9]
    ...
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Creation complete after 12s [id=i-046a115228b08ed10]
    
    Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
    
    Outputs:
    ec2_public_ip = "3.64.13.241"
    ...
    + ssh -o StrictHostKeyChecking=no ec2-user@3.64.13.241 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.12-4 emrearabacioglu ****
    ...
    Login Succeeded
    Image emrearabacioglu/demo-app:1.1.12-4 Pulled 
    Image postgres:16 Pulled 
    Container ec2-user-postgres-1 Started
    success
    ...
    Finished: SUCCESS

#### Remote State Verification
Ran `terraform init` locally in the same folder. It connected to the same S3 backend, and `terraform state list` showed the resources Jenkins had created:

    root@PC:~/modules/terraform/java-terraform (master)# cd terraform/
    root@PC:~/modules/terraform/java-terraform/terraform (master)# terraform init
    Initializing the backend...
    
    Successfully configured the backend "s3"! Terraform will automatically
    use this backend unless the backend configuration changes.
    ...
    Terraform has been successfully initialized!
    
    root@PC:~/modules/terraform/java-terraform/terraform (master)# terraform state list
    data.aws_ami.latest-amazon-linux-image
    aws_default_route_table.main-rtb
    aws_default_security_group.default-sg
    aws_instance.myapp-server
    aws_internet_gateway.myapp-igw
    aws_subnet.myapp-subnet-1
    aws_vpc.myapp-vpc

<img width="1907" height="546" alt="image" src="https://github.com/user-attachments/assets/e5011bed-271e-4e43-9bb3-7e7aa5041282" />
