### Exercises for Module "AWS Services"

**Business Case:** Your company has decided that they will use AWS as a cloud provider to deploy their applications. It's too much overhead to manage multiple platforms, including the billing etc.

So you need to deploy the previous NodeJS application on an EC2 instance now. This means you need to create and prepare an EC2 server with the AWS Command Line Tool to run your NodeJS app container on it.







******

<details>
<summary>EXERCISE 1: Create IAM user</summary>
 <br />
 
**Case:** You need an IAM user with correct permissions to execute the tasks below.
 
**Objectives:**
* Create a new IAM user using "your name" as a username and "devops" as the user-group

  ↳ **Execution:**
  <img width="1518" height="683" alt="image" src="https://github.com/user-attachments/assets/346faa3a-aebf-4965-ad96-4603b33b8f41" />
  <img width="1508" height="629" alt="image" src="https://github.com/user-attachments/assets/e164a825-ed08-4b4d-a1c6-214f65db82a2" />

* Give the "devops" group all needed permissions to execute the tasks below - with login and CLI credentials

  ↳ **Execution:**
  <img width="1508" height="723" alt="image" src="https://github.com/user-attachments/assets/4eea146a-44f4-4006-8e2d-738a80e01900" />

</details>

******

<details>
<summary>EXERCISE 2: Configure AWS CLI</summary>

 <br />
 
**Case:** You want to use the AWS CLI for the following tasks. So, to be able to interact with the AWS account from the AWS Command Line tool you need to configure it correctly.
 
**Objectives:**
* Set credentials for that user for AWS CLI
  
  ↳ **Execution:**
  <img width="1506" height="801" alt="image" src="https://github.com/user-attachments/assets/14594074-d393-43ff-a3f5-bd12b5c96916" />

* Configure correct region for your AWS CLI

  ↳ **Execution:**
  ```bash
  root@PC:~# aws configure
  AWS Access Key ID [****************QHCO]: ********
  AWS Secret Access Key [****************b8EN]: ********
  Default region name [eu-central-1]: eu-central-1
  Default output format [json]: json
  ```

</details>

******

<details>
<summary>EXERCISE 3: Create VPC</summary>
 <br />
 
**Case:** You want to create the EC2 Instance in a dedicated VPC, instead of using the default one. So, using the AWS CLI.

**Objectives:**

* Create a new VPC with 1 subnet
* Create a security group in the VPC that will allow you access on ssh port 22 and will allow browser access to your Node application

  ↳ **Execution:**
  ```bash
  root@PC:~# aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query "Vpc.VpcId" --output text
  vpc-03938a0e40ef6d9a6
  root@PC:~# aws ec2 create-subnet --vpc-id vpc-03938a0e40ef6d9a6 --cidr-block 10.0.1.0/24 --query "Subnet.SubnetId" --output text
  subnet-0896787fecbb68808
  root@PC:~# aws ec2 create-security-group --group-name devops-sg --description "SG for devops" --vpc-id vpc-03938a0e40ef6d9a6 --query "GroupId" --output text
  sg-054c25198e70e49d6
  root@PC:~# aws ec2 authorize-security-group-ingress --group-id sg-054c25198e70e49d6 --protocol tcp --port 22 --cidr 195.
  174.90.118/32
  {
      "Return": true,
      "SecurityGroupRules": [
          {
              "SecurityGroupRuleId": "sgr-0004b2728a08f2ef3",
              "GroupId": "sg-054c25198e70e49d6",
              "GroupOwnerId": "731872836472",
              "IsEgress": false,
              "IpProtocol": "tcp",
              "FromPort": 22,
              "ToPort": 22,
              "CidrIpv4": "195.174.90.118/32",
              "SecurityGroupRuleArn": "arn:aws:ec2:eu-central-1:731872836472:security-group-rule/sgr-0004b2728a08f2ef3"
          }
      ]
  }
  
  ```

</details>

******

<details>
<summary>EXERCISE 4: Create EC2 Instance</summary>
 <br />

**Objectives:**

* Create an EC2 instance in that VPC with the security group you just created and ssh key file

  ↳ **Execution:**
```bash

root@PC:~# aws ec2 create-key-pair --key-name devops-key --query "KeyMaterial" --output text > devops-key.pem
root@PC:~# mv devops-key.pem ~/.ssh/
root@PC:~# sudo chmod 400 ~/.ssh/devops-key.pem
root@PC:~# ls -l ~/.ssh/devops-key.pem
-r-------- 1 root root 1679 Jun 14 13:44 /root/.ssh/devops-key.pem
root@PC:~# aws ec2 run-instances --image-id ami-036bdae36143a955f \
> --count 1 \
> --instance-type t2.micro \
> --key-name devops-key \
> --security-group-ids sg-054c25198e70e49d6 \
> --subnet-id subnet-0896787fecbb68808
{
    "ReservationId": "r-0c91710e9a1c316e8",
    "OwnerId": "731872836472",
    "Groups": [],
    "Instances": [
        {
            "Architecture": "x86_64",
            "BlockDeviceMappings": [],
            "ClientToken": "c7a1bbfd-3b6f-4925-bbf4-e25dc17a28c4",
            "EbsOptimized": false,
            "EnaSupport": true,
            "Hypervisor": "xen",
            "NetworkInterfaces": [
                {
                    "Attachment": {
                        "AttachTime": "2026-06-14T10:49:07+00:00",
                        "AttachmentId": "eni-attach-0cf10de08abfc013b",
                        "DeleteOnTermination": true,
                        "DeviceIndex": 0,
                        "Status": "attaching",
                        "NetworkCardIndex": 0
                    },
                    "Description": "",
                    "Groups": [
                        {
                            "GroupId": "sg-054c25198e70e49d6",
                            "GroupName": "devops-sg"
                        }
                    ],
                    "Ipv6Addresses": [],
                    "MacAddress": "02:81:2f:bb:10:29",
                    "NetworkInterfaceId": "eni-0d4d72750f5389bf7",
                    "OwnerId": "731872836472",
                    "PrivateIpAddress": "10.0.1.129",
                    "PrivateIpAddresses": [
                        {
                            "Primary": true,
                            "PrivateIpAddress": "10.0.1.129"
                        }
                    ],
                    "SourceDestCheck": true,
                    "Status": "in-use",
                    "SubnetId": "subnet-0896787fecbb68808",
                    "VpcId": "vpc-03938a0e40ef6d9a6",
                    "InterfaceType": "interface",
                    "Operator": {
                        "Managed": false
                    }
                }
            ],
            "RootDeviceName": "/dev/xvda",
            "RootDeviceType": "ebs",
            "SecurityGroups": [
                {
                    "GroupId": "sg-054c25198e70e49d6",
                    "GroupName": "devops-sg"
                }
            ],
            "SourceDestCheck": true,
            "StateReason": {
                "Code": "pending",
                "Message": "pending"
            },
            "VirtualizationType": "hvm",
            "CpuOptions": {
                "CoreCount": 1,
                "ThreadsPerCore": 1
            },
            "CapacityReservationSpecification": {
                "CapacityReservationPreference": "open"
            },
            "MetadataOptions": {
                "State": "pending",
                "HttpTokens": "required",
                "HttpPutResponseHopLimit": 2,
                "HttpEndpoint": "enabled",
                "HttpProtocolIpv6": "disabled",
                "InstanceMetadataTags": "disabled"
            },
            "EnclaveOptions": {
                "Enabled": false
            },
            "BootMode": "uefi-preferred",
            "PrivateDnsNameOptions": {
                "HostnameType": "ip-name",
                "EnableResourceNameDnsARecord": false,
                "EnableResourceNameDnsAAAARecord": false
            },
            "MaintenanceOptions": {
                "AutoRecovery": "default",
                "RebootMigration": "default"
            },
            "CurrentInstanceBootMode": "legacy-bios",
            "Operator": {
                "Managed": false
            },
            "InstanceId": "i-02cbe09bcc47af8a4",
            "ImageId": "ami-036bdae36143a955f",
            "State": {
                "Code": 0,
                "Name": "pending"
            },
            "PrivateDnsName": "ip-10-0-1-129.eu-central-1.compute.internal",
            "PublicDnsName": "",
            "StateTransitionReason": "",
            "KeyName": "devops-key",
            "AmiLaunchIndex": 0,
            "ProductCodes": [],
            "InstanceType": "t2.micro",
            "LaunchTime": "2026-06-14T10:49:07+00:00",
            "Placement": {
                "AvailabilityZoneId": "euc1-az2",
                "GroupName": "",
                "Tenancy": "default",
                "AvailabilityZone": "eu-central-1a"
            },
            "Monitoring": {
                "State": "disabled"
            },
            "SubnetId": "subnet-0896787fecbb68808",
            "VpcId": "vpc-03938a0e40ef6d9a6",
            "PrivateIpAddress": "10.0.1.129"
        }
    ]
}
(END)

```



</details>

******

<details>
<summary>EXERCISE 5: SSH into the server and install Docker on it</summary>
 <br />
 
**Case:** Once the EC2 instance is created successfully, you want to prepare the server to run Docker containers.
 
**Objectives:**

* SSH into the server
* Install Docker on it to run the dockerized application later

  ↳ **Execution:**
```bash
root@PC:~# aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].PublicIpAddress" --output text
root@PC:~# aws ec2 create-internet-gateway --query "InternetGateway.InternetGatewayId" --output text
igw-06a69241d399ef983
root@PC:~# aws ec2 attach-internet-gateway --vpc-id vpc-03938a0e40ef6d9a6 --internet-gateway-id igw-06a69241d399ef983
root@PC:~# aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-03938a0e40ef6d9a6" --query "RouteTables[0].RouteTableId" --output text
rtb-085980d63e7dc74fc
root@PC:~# aws ec2 create-route --route-table-id rtb-085980d63e7dc74fc --destination-cidr-block 0.0.0.0/0 --gateway-id igw-06a69241d399ef983
{
    "Return": true
}
root@PC:~# aws ec2 allocate-address --domain vpc --query "AllocationId" --output text
eipalloc-0fa3bcf93ca21e83c
root@PC:~# aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].InstanceId" --output text
i-02cbe09bcc47af8a4
root@PC:~# aws ec2 associate-address --instance-id i-02cbe09bcc47af8a4 --allocation-id eipalloc-0fa3bcf93ca21e83c
{
    "AssociationId": "eipassoc-0bbced44faba11de6"
}
root@PC:~# aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].PublicIpAddress" --output text
63.186.60.132
root@PC:~# ssh -i "~/.ssh/devops-key.pem" ec2-user@63.186.60.132
Warning: Identity file devops-key.pem not accessible: No such file or directory.
The authenticity of host '63.186.60.132 (63.186.60.132)' can't be established.
ED25519 key fingerprint is SHA256:oMxB0V70uBnxLAApfefr7JXR8W5h66MQoXatD7u9Bc4.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '63.186.60.132' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
[ec2-user@ip-10-0-1-129 ~]$
[ec2-user@ip-10-0-1-129 ~]$
[ec2-user@ip-10-0-1-129 ~]$
[ec2-user@ip-10-0-1-129 ~]$
[ec2-user@ip-10-0-1-129 ~]$ sudo apt-get update
sudo: apt-get: command not found
[ec2-user@ip-10-0-1-129 ~]$ apt-get update
-bash: apt-get: command not found
[ec2-user@ip-10-0-1-129 ~]$ sudo dnf update -y
Amazon Linux 2023 repository                                                                                                                  63 MB/s |  64 MB     00:01
...
Complete!
[ec2-user@ip-10-0-1-129 ~]$ sudo dnf install docker -y
Last metadata expiration check: 0:00:05 ago on Sun Jun 14 11:13:43 2026.
...
Complete!
[ec2-user@ip-10-0-1-129 ~]$ sudo systemctl start docker
[ec2-user@ip-10-0-1-129 ~]$ sudo systemctl enable docker
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /usr/lib/systemd/system/docker.service.
[ec2-user@ip-10-0-1-129 ~]$ sudo usermod -aG docker ec2-user
[ec2-user@ip-10-0-1-129 ~]$ docker ps
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.44/containers/json": dial unix /var/run/docker.sock: connect: permission denied
[ec2-user@ip-10-0-1-129 ~]$ exit
logout
Connection to 63.186.60.132 closed.
root@PC:~# ssh -i "~/.ssh/devops-key.pem" ec2-user@63.186.60.132
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
Last login: Sun Jun 14 11:10:59 2026 from 195.174.90.118
[ec2-user@ip-10-0-1-129 ~]$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
[ec2-user@ip-10-0-1-129 ~]$ exit
logout
Connection to 63.186.60.132 closed.
root@PC:~#


```

</details>

******

### Set up Continuous Deployment


**Business Case:** Now you don't want to deploy manually to the server all the time, because it's time-consuming and also sometimes you miss it, when changes are made and the new docker image is built by the pipeline. When you forget to check the pipeline, your team members need to write you and ask you to deploy the new version.

As a solution, you want to automate this thing to save you and your team members time and energy.



******

<details>
<summary>EXERCISE 6: Add docker-compose for deployment</summary>
 <br />

**Objectives:**

* Add docker-compose to your NodeJS application

This is because you want to have the whole configuration for starting the docker container in a file, in case you need to make change or add a database later, instead of a plain docker command with parameters.

Use repository: https://gitlab.com/twn-devops-bootcamp/latest/09-aws/aws-exercises

↳ **Execution:**
<img width="1568" height="341" alt="image" src="https://github.com/user-attachments/assets/54b715c2-af8c-45e1-b39d-7e4bbad680c0" />



</details>

******

<details>
<summary>EXERCISE 7: Add "deploy to EC2" step to your existing pipeline</summary>
 <br />
 
 **Objectives:**
 
* Add a deployment step to the Jenkinsfile from the previous exercise’s project to deploy to EC2.

  ↳ **Execution:**

  **Jenkinsfile:**
```groovy

pipeline {
    agent any
    tools {
        nodejs "my-nodejs"
    }
    environment {
        DOCKER_USER = "emrearabacioglu"
        IMAGE_NAME = "${DOCKER_USER}/nodejs-app:1.0.${BUILD_NUMBER}"
    }
    stages {
        stage('increment version') {
            steps {
                dir('app') {
                    sh 'npm version patch'
                }
            }
        }
        stage('Run tests') {
            steps {
                dir('app') {
                    sh 'npm install'
                    sh 'npm test'
                }
            }
        }
        stage('Build and Push docker image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-repo', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "docker build -t ${IMAGE_NAME} ."
                    sh "echo ${PASS} | docker login -u ${USER} --password-stdin"
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }
        stage('deploy to EC2') {
            steps {
                script {
                   def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME}"
                   def ec2Instance = "ec2-user@63.186.60.132"

                   sshagent(['ec2-server-key']) {
                       sh "scp -o StrictHostKeyChecking=no server-cmds.sh ${ec2Instance}:/home/ec2-user"
                       sh "scp -o StrictHostKeyChecking=no docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                       sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                   }     
                }
            }
        }
        stage('commit version update') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh 'git config --global user.email "jenkins@example.com"'
                    sh 'git config --global user.name "Jenkins"'
                    sh 'git add app/package.json app/package-lock.json'
                    sh 'git commit -m "ci: version bump"'
                    sh "git push https://${USER}:${PASS}@github.com/emrearabacioglu/aws-exercises HEAD:main"
                }
            }
        }
    }     
}

```

**Build successful:**

<img width="1160" height="271" alt="image" src="https://github.com/user-attachments/assets/a4b56a8b-3a87-4858-a265-669a48e4d479" />

**Terminal verification:**

```bash
[ec2-user@ip-10-0-1-129 ~]$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED          STATUS          PORTS                                       NAMES
db7e18fecb63   emrearabacioglu/nodejs-app:1.0.5   "docker-entrypoint.s…"   16 seconds ago   Up 14 seconds   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   ec2-user-nodejs-app-1
[ec2-user@ip-10-0-1-129 ~]$

```

</details>

******

<details>
<summary>EXERCISE 8: Configure access from browser (EC2 Security Group)</summary>
 <br />
 
**Case:** After executing the Jenkins pipeline successfully, the application is deployed, but you still can't access it from the browser. You need to open the correct port on the server. For that, using the AWS CLI,

**Objectives:**

* Configure the EC2 security group to access your application from a browser

  ↳ **Execution:**

```bash

  root@PC:~# aws ec2 describe-instances --filters "Name=ip-address,Values=63.186.60.132" --query "Reservations[*].Instances[*].SecurityGroups[*].GroupId" --output text
sg-054c25198e70e49d6
root@PC:~# aws ec2 authorize-security-group-ingress --group-id sg-054c25198e70e49d6 --protocol tcp --port 3000 --cidr 0.0.0.0/0
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-05aba93134a13d161",
            "GroupId": "sg-054c25198e70e49d6",
            "GroupOwnerId": "731872836472",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 3000,
            "ToPort": 3000,
            "CidrIpv4": "0.0.0.0/0",
            "SecurityGroupRuleArn": "arn:aws:ec2:eu-central-1:731872836472:security-group-rule/sgr-05aba93134a13d161"
        }
    ]
}
root@PC:~#

```
**Browser Connection:**

<img width="883" height="626" alt="image" src="https://github.com/user-attachments/assets/c5aa6122-4627-44a2-b85a-a1d68a8771df" />

</details>

******

<details>
<summary>EXERCISE 9: Configure automatic triggering of multi-branch pipeline</summary>
 <br />

**Case:** Your team members are creating branches to add new features to the application or fix any issues, so you don't want to build and deploy these half-done features or bug fixes. You want to build and deploy only to the master branch. All other branches should only run tests. Add this logic to the Jenkinsfile:

**Objectives:**

* Add branch based logic to Jenkinsfile
* Add webhook to trigger pipeline automatically

↳ **Execution:**

Configured the Jenkinsfile to restrict image building and EC2 deployment exclusively to the `main` branch, ensuring feature branches only execute automated tests. Implemented a safeguard using the `changelog` parameter to automatically ignore `ci: version bump` commits, effectively preventing infinite build loops triggered by the pipeline's own repository updates.

**Jenkinsfile:**

```groovy

pipeline {
    agent any
    tools {
        nodejs "my-nodejs"
    }
    environment {
        DOCKER_USER = "emrearabacioglu"
        IMAGE_NAME = "${DOCKER_USER}/nodejs-app:1.0.${BUILD_NUMBER}"
    }
    stages {
        stage('increment version') {
            when { 
                not { changelog '.*ci: version bump.*' } 
            }
            steps {
                dir('app') {
                    sh 'npm version patch'
                }
            }
        }
        stage('Run tests') {
            when { 
                not { changelog '.*ci: version bump.*' } 
            }
            steps {
                dir('app') {
                    sh 'npm install'
                    sh 'npm test'
                }
            }
        }
        stage('Build and Push docker image') {
            when { 
                allOf {
                    branch 'main'
                    not { changelog '.*ci: version bump.*' }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-repo', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "docker build -t ${IMAGE_NAME} ."
                    sh "echo ${PASS} | docker login -u ${USER} --password-stdin"
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }
        stage('deploy to EC2') {
            when { 
                allOf {
                    branch 'main'
                    not { changelog '.*ci: version bump.*' }
                }
            }
            steps {
                script {
                   def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME}"
                   def ec2Instance = "ec2-user@63.186.60.132"

                   sshagent(['ec2-server-key']) {
                       sh "scp -o StrictHostKeyChecking=no server-cmds.sh ${ec2Instance}:/home/ec2-user"
                       sh "scp -o StrictHostKeyChecking=no docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                       sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                   }     
                }
            }
        }
        stage('commit version update') {
            when { 
                allOf {
                    branch 'main'
                    not { changelog '.*ci: version bump.*' }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh 'git config --global user.email "jenkins@example.com"'
                    sh 'git config --global user.name "Jenkins"'
                    sh 'git add app/package.json app/package-lock.json'
                    sh 'git commit -m "ci: version bump"'
                    sh "git push https://${USER}:${PASS}@github.com/emrearabacioglu/aws-exercises HEAD:main"
                }
            }
        }
    }     
}
```

**Webhook:**

<img width="1380" height="435" alt="image" src="https://github.com/user-attachments/assets/a181bd92-2c31-4ffd-890e-fdcf7cc97f89" />


</details>

