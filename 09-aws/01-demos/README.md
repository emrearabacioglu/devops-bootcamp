# Module 9 – AWS Services

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Deploy Web Application on EC2 Instance (manually) | Create an EC2 instance, install Docker, run an image from Docker Hub |
| 2 | CD – Deploy Application from Jenkins Pipeline to EC2 Instance (docker) | Jenkins connects to EC2 over SSH and runs `docker run` |
| 3 | CD – Deploy Application from Jenkins Pipeline on EC2 Instance (docker-compose) | Deploy app + Postgres with Docker Compose, commands moved to `server-cmds.sh` |
| 4 | Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning) | Version bump → build → push → deploy → commit version back to Git |
| 5 | Create repository on AWS and push to private Docker registry | Push a Node.js image to Amazon ECR |
| 6 | Interacting with AWS CLI | Create SG, key pair, EC2 instance, IAM user/group/policy with the CLI |

## Takeaways

- **SSH key:** `chmod 400 key.pem` before `ssh -i`. In WSL, `chmod` doesn't work on `/mnt/c/...`, so copy the key to `~/.ssh` first.
- **Docker without sudo on EC2:** `sudo usermod -aG docker $USER`.
- **Jenkins → EC2:** SSH Agent plugin + an "SSH Username with private key" credential. Wrap the commands in `sshagent(['ec2-server-key']) { ... }` and use `-o StrictHostKeyChecking=no` on the first connection. The EC2 security group must allow port 22 from the Jenkins server IP.
- **Many remote commands:** put them in a script (`server-cmds.sh`), copy it and `docker-compose.yaml` with `scp`, run it with `ssh ... bash ./server-cmds.sh <args>`.
- **Dynamic image in compose:** `image: ${IMAGE}` in `docker-compose.yaml` + `export IMAGE=$1` in the script.
- **Commit from Jenkins:** Jenkins checks out a detached HEAD, so push with `git push origin HEAD:<branch>`.
- **ECR login:** `aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <registry>`. The image must be tagged with the full registry URL before `docker push`.
- **AWS CLI output:** `--filters` narrows the result, `--query` (JMESPath) picks fields. `create-key-pair --query 'KeyMaterial' --output text > key.pem` saves the private key.
- **Test another user's permissions:** `export AWS_ACCESS_KEY_ID=...` and `AWS_SECRET_ACCESS_KEY=...` override `~/.aws/credentials` for that shell.

******

<details>
<summary>Demo Project: Deploy Web Application on EC2 Instance (manually)</summary>
 <br />

### Demo Executed: Run a Docker image on an EC2 instance

#### EC2 Instance Creation
Created an Amazon Linux 2023 instance from the AWS console and downloaded the key pair.

<img width="1913" height="817" alt="image" src="https://github.com/user-attachments/assets/f35608d7-b6c5-4f1a-81e1-334d3583192f" />

#### SSH Access
Restricted the key permissions and connected to the instance:

    root@PC:~/.ssh# chmod 400 docker-server.pem
    root@PC:~/.ssh# ssh -i docker-server.pem ec2-user@3.65.227.116
    ...
    [ec2-user@ip-172-31-21-191 ~]$ whoami
    ec2-user

#### Docker Installation
Installed and started Docker, then added `ec2-user` to the docker group to run Docker without `sudo`:

    [ec2-user@ip-172-31-21-191 ~]$ sudo yum install docker
    ...
    Installed:
      docker-25.0.14-1.amzn2023.0.5.x86_64
    Complete!

    [ec2-user@ip-172-31-21-191 ~]$ sudo service docker start
    [ec2-user@ip-172-31-21-191 ~]$ sudo usermod -aG docker $USER

#### Running the App
Logged in to Docker Hub, pulled my image and started it. Host port 3000 maps to container port 3080:

    [ec2-user@ip-172-31-21-191 ~]$ docker login
    Username: emrearabacioglu
    Login Succeeded

    [ec2-user@ip-172-31-21-191 ~]$ docker pull emrearabacioglu/demo-image:v1
    Status: Downloaded newer image for emrearabacioglu/demo-image:v1

    [ec2-user@ip-172-31-21-191 ~]$ docker run -d -p 3000:3080 emrearabacioglu/demo-image:v1

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS         PORTS                                         NAMES
    59c32091ca90   emrearabacioglu/demo-image:v1   "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds   0.0.0.0:3000->3080/tcp, :::3000->3080/tcp   sharp_goldberg

#### Security Group
Opened the app port in the security group to reach the app from the browser:

<img width="1664" height="271" alt="image" src="https://github.com/user-attachments/assets/61cbbb66-02c7-447e-8ad6-0299b45b6098" />
<img width="1911" height="545" alt="image" src="https://github.com/user-attachments/assets/92090a65-6fc0-4e18-8740-6d197d9ea650" />

</details>

******

<details>
<summary>Demo Project: CD – Deploy Application from Jenkins Pipeline to EC2 Instance (automatically with docker)</summary>
 <br />

### Demo Executed: Jenkins deploys the image to EC2 over SSH

#### Setup
- Installed the **SSH Agent** plugin in Jenkins and added the EC2 key as an "SSH Username with private key" credential (`ec2-server-key`, user `ec2-user`).
- Opened port 22 for the Jenkins server IP in the EC2 security group.
- Added a deploy stage to the multibranch pipeline that runs `docker run` on EC2 with `ssh`.

#### Run 1: Existing image
The deploy stage pulled `demo-app:1.1.1-10` and started it on port 3080:

    [ssh-agent] Using credentials ec2-user
    [ssh-agent] Started.
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 docker run -p 3080:8080 -d emrearabacioglu/demo-app:1.1.1-10
    Unable to find image 'emrearabacioglu/demo-app:1.1.1-10' locally
    Status: Downloaded newer image for emrearabacioglu/demo-app:1.1.1-10
    ...
    Finished: SUCCESS

<img width="788" height="207" alt="image" src="https://github.com/user-attachments/assets/78dc0ff3-a153-443a-b78c-eca206dc4dcb" />

#### Run 2: Full pipeline with the shared library
The pipeline used my `jenkins-shared-library` (buildJar, buildImage, dockerLogin, dockerPush). It built the jar, built and pushed `jma-3.0`, then started it on EC2 on port 8080.

Build and push:

    + mvn package
    ...
    [INFO] Building jar: /var/jenkins_home/workspace/ultibranch-pipeline_jenkins-jobs/target/java-maven-app-1.1.8.jar
    [INFO] BUILD SUCCESS
    ...
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    + docker push emrearabacioglu/demo-app:jma-3.0
    ...
    jma-3.0: digest: sha256:4b8fad7e4f861372149685a8b1a2fd18e5496c5e5657dcc8fc4d61250b5af05b size: 1159

Deploy:

    deploying docker image to EC2...
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 docker run -p 8080:8080 -d emrearabacioglu/demo-app:jma-3.0
    Status: Downloaded newer image for emrearabacioglu/demo-app:jma-3.0
    ...
    Finished: SUCCESS

Both containers running on the server:

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                              COMMAND                  CREATED         STATUS          PORTS                                       NAMES
    27b02fffdd94   emrearabacioglu/demo-app:jma-3.0    "/bin/sh -c 'java -j…"   7 minutes ago   Up 40 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   friendly_hamilton
    28479044591b   emrearabacioglu/demo-app:1.1.1-10   "/bin/sh -c 'java -j…"   6 hours ago     Up 6 hours      0.0.0.0:3080->8080/tcp, :::3080->8080/tcp   sweet_feynman

<img width="883" height="212" alt="image" src="https://github.com/user-attachments/assets/804510fb-86b4-4c6a-b293-a8791a4452b7" />

</details>

******

<details>
<summary>Demo Project: CD – Deploy Application from Jenkins Pipeline on EC2 Instance (automatically with docker-compose)</summary>
 <br />

### Demo Executed: Deploy the app and Postgres with Docker Compose

#### Overview
Replaced `docker run` with Docker Compose so the app and a Postgres container start together. The remote commands moved into `server-cmds.sh`. Jenkins copies the script and the compose file to EC2 and runs the script.

#### Files

`Jenkinsfile`:

```groovy
#!/usr/bin/env groovy

library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
    [$class: 'GitSCMSource',
    remote: 'https://github.com/emrearabacioglu/jenkins-shared-library.git',
    credentialsID: 'github-credentials'
    ]
)

pipeline {
    agent any
    tools {
        maven 'maven-3.9'
    }
    environment {
        IMAGE_NAME = 'emrearabacioglu/demo-app:jma-3.0'
    }
    stages {
        stage('build app') {
            steps {
                echo 'building application jar...'
                buildJar()
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
        stage("deploy") {
            steps {
                script {
                    echo 'deploying docker image to EC2...'
                    def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME}"
                    def ec2Instance = "ec2-user@3.125.50.166"
                    sshagent(['ec2-server-key']) {
                        sh "scp server-cmds.sh ${ec2Instance}:/home/ec2-user"
                        sh "scp docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                        sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                    }
                }
            }               
        }
    }
}
```

`docker-compose.yaml`:

```yaml
version: '3.8'
services:
  java-maven-app:
    image: ${IMAGE}
    ports:
      - 8080:8080

  postgres:
    image: postgres:15
    ports:
      - 5432:5432
    environment:
      - POSTGRES_PASSWORD=my-pwd
```

`server-cmds.sh`:

```bash
#!/usr/bin/env groovy

export IMAGE=$1

docker-compose -f docker-compose.yaml up --detach

echo "success"
```

#### Pipeline Run
Build and push (same as before):

    + mvn package
    ...
    [INFO] BUILD SUCCESS
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    + docker push emrearabacioglu/demo-app:jma-3.0
    ...
    jma-3.0: digest: sha256:92fb82f7fbe3673c80b8b5bb6a870e266f11e7919d4bf2618ed760e4f1d2ff59 size: 1159

Copied the files to EC2 and ran the script:

    + scp server-cmds.sh ec2-user@3.125.50.166:/home/ec2-user
    + scp docker-compose.yaml ec2-user@3.125.50.166:/home/ec2-user
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 bash ./server-cmds.sh emrearabacioglu/demo-app:jma-3.0

Docker Compose created the network and both containers:

     Network ec2-user_default Created
     ...
     Container ec2-user-postgres-1 Created
     ...
     Container ec2-user-java-maven-app-1 Started
     Container ec2-user-postgres-1 Started
    success

<img width="899" height="220" alt="image" src="https://github.com/user-attachments/assets/79e4c947-ec71-4918-a989-739a326fd7eb" />

Result on the server:

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                              COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    b40cea0f15dd   emrearabacioglu/demo-app:jma-3.0   "/bin/sh -c 'java -j…"   20 seconds ago   Up 18 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
    020d64f33101   postgres:15                        "docker-entrypoint.s…"   20 seconds ago   Up 18 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1

</details>

******

<details>
<summary>Demo Project: Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning)</summary>
 <br />

### Demo Executed: Full pipeline with dynamic versioning

#### Overview
Added two stages to the previous pipeline: **increment version** at the start and **commit version update** at the end. Each run bumps the patch version in `pom.xml`, tags the image as `<version>-<build number>`, deploys it with Docker Compose and pushes the new `pom.xml` back to GitHub. `docker-compose.yaml` and `server-cmds.sh` are the same as in the previous project.

#### Jenkinsfile

```groovy
#!/usr/bin/env groovy

library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
    [$class: 'GitSCMSource',
    remote: 'https://github.com/emrearabacioglu/jenkins-shared-library.git',
    credentialsID: 'github-credentials'
    ]
)

pipeline {
    agent any
    tools {
        maven 'maven-3.9'
    }
    stages {
        stage('increment version'){
            steps {
                script {
                    echo 'incrementing the version..'
                    sh 'mvn build-helper:parse-version versions:set \
                        -DnewVersion=\\\${parsedVersion.majorVersion}.\\\${parsedVersion.minorVersion}.\\\${parsedVersion.nextIncrementalVersion} \
                        versions:commit'
                    def matcher = readFile('pom.xml') =~ '<version>(.+)</version>'
                    def version = matcher[0][1]
                    env.IMAGE_NAME = "emrearabacioglu/demo-app:${version}-${BUILD_NUMBER}"
                }
            }
        }
        stage('build app') {
            steps {
                echo 'building application jar...'
                buildJar()
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
        stage("deploy") {
            steps {
                script {
                    echo 'deploying docker image to EC2...'

                    def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME}"
                    def ec2Instance = "ec2-user@3.125.50.166"

                    sshagent(['ec2-server-key']) {
                        sh "scp server-cmds.sh ${ec2Instance}:/home/ec2-user"
                        sh "scp docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                        sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                    }
                }
            }               
        }
        stage('commit version update') {
            steps{
                script{
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                        sh "git remote set-url origin https://${USER}:${PASS}@github.com/emrearabacioglu/java-maven-app.git"
                        sh 'git add .'
                        sh 'git commit -m "version bump"'
                        sh 'git push origin HEAD:jenkins-jobs'
                    }
                }
            }
        }
    }
}
```

#### Pipeline Run
Version bumped from 1.1.8 to 1.1.9:

    + mvn build-helper:parse-version versions:set -DnewVersion=${parsedVersion.majorVersion}.${parsedVersion.minorVersion}.${parsedVersion.nextIncrementalVersion} versions:commit
    ...
    [INFO] Processing change of com.example:java-maven-app:1.1.8 -> 1.1.9

Image built and pushed with the new tag (`1.1.9-12` = version + build number):

    + docker build -t emrearabacioglu/demo-app:1.1.9-12 .
    + docker push emrearabacioglu/demo-app:1.1.9-12
    ...
    1.1.9-12: digest: sha256:915a34770f02767d81762efd3bd92538db2e68abceffcd27210db69475995817 size: 1159

Docker Compose replaced the app container with the new image:

    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.9-12
    ...
     Image emrearabacioglu/demo-app:1.1.9-12 Pulled
     Container ec2-user-java-maven-app-1 Recreated
     ...
     Container ec2-user-postgres-1 Started
     Container ec2-user-java-maven-app-1 Started
    success

Version bump committed and pushed to the `jenkins-jobs` branch:

    + git commit -m version bump
    [detached HEAD 034949a] version bump
    + git push origin HEAD:jenkins-jobs
    To https://github.com/emrearabacioglu/java-maven-app.git
       f1fe8e6..034949a  HEAD -> jenkins-jobs

<img width="1184" height="265" alt="image" src="https://github.com/user-attachments/assets/0b5cf21a-dc6c-42e1-bf26-a424006f8c97" />

Result on the server:

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    42d798c26a0e   emrearabacioglu/demo-app:1.1.9-12   "/bin/sh -c 'java -j…"   36 seconds ago   Up 34 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
    020d64f33101   postgres:15                         "docker-entrypoint.s…"   24 hours ago     Up 34 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1

</details>

******

<details>
<summary>Demo Project: Create repository on AWS and push to private Docker registry</summary>
 <br />

### Demo Executed: Push a Node.js image to Amazon ECR

#### Overview
Created a private ECR repository (`my-app`), logged Docker in to ECR with the AWS CLI, and pushed two versions of the Node.js app image.

#### Docker Login to ECR
Configured the AWS CLI, then passed the ECR token to `docker login`:

    root@PC:/mnt/c/Users/emrea# aws configure
    AWS Access Key ID [****************6472]: ******
    AWS Secret Access Key [****************VPGR]: ******
    Default region name [eu-central-1]: eu-central-1
    Default output format [json]: json

    root@PC:/mnt/c/Users/emrea# aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded

#### Build, Tag and Push
Version `1.0`. The image is tagged with the full ECR URL before pushing:

    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.0 .
    ...
    root@PC:/mnt/c/Users/emrea# docker tag my-app:1.0 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    root@PC:/mnt/c/Users/emrea# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    ...
    1.0: digest: sha256:6864de50df6c69649d7fad5dbeab0c774ba73873004dfd7d925a9bd831892474 size: 856

Version `1.1`, same steps:

    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.1 .
    ...
    root@PC:/mnt/c/Users/emrea/js-app# docker tag my-app:1.1 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    ...
    1.1: digest: sha256:b66fee87f8f9fd58d93f7b97329648f34b2957975fb0f00e74af64be5c1aab20 size: 856

Both tags in the ECR repository:

<img width="1631" height="624" alt="image" src="https://github.com/user-attachments/assets/4c8b9763-6c25-423c-b4bb-a2d74dfffbbb" />

</details>

******

<details>
<summary>Demo Project: Interacting with AWS CLI</summary>
 <br />

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

</details>

******
