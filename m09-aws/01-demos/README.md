******

<details>
<summary>Introduction to EC2 Virtual Cloud Server</summary>
 <br />
 
### AWS EC2 & Docker WebApp Deployment

#### EC2 Instance Creation

<img width="1913" height="817" alt="image" src="https://github.com/user-attachments/assets/f35608d7-b6c5-4f1a-81e1-334d3583192f" />


#### SSH Key Configuration and Instance Access
Configured the downloaded private key with the required strict permissions and successfully established a secure SSH connection to the provisioned Amazon Linux 2023 EC2 instance.

    root@PC:~/.ssh# chmod 400 docker-server.pem
    root@PC:~/.ssh# ssh -i docker-server.pem ec2-user@3.65.227.116
    The authenticity of host '3.65.227.116 (3.65.227.116)' can't be established.
    Warning: Permanently added '3.65.227.116' (ED25519) to the list of known hosts.
       ,     #_
       ~\_  ####_        Amazon Linux 2023
     ~~  \_#####\
     ~~     \###|
     ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
    [ec2-user@ip-172-31-21-191 ~]$ whoami
    ec2-user

#### Docker Environment Setup
Updated the package manager, installed the Docker engine, initiated the service, and appended the default `ec2-user` to the Docker group to enable container execution without root privileges.

    [ec2-user@ip-172-31-21-191 ~]$ sudo yum install docker
    ...
    Installed:
      docker-25.0.14-1.amzn2023.0.5.x86_64
    Complete!
    
    [ec2-user@ip-172-31-21-191 ~]$ sudo service docker start
    Redirecting to /bin/systemctl start docker.service
    
    [ec2-user@ip-172-31-21-191 ~]$ sudo usermod -aG docker $USER

#### Container Deployment
Authenticated with the private DockerHub registry, pulled the previously built custom web application image, and deployed it in detached mode. The application was exposed by mapping the host port 3000 to the container port 3080.

    [ec2-user@ip-172-31-21-191 ~]$ docker login
    Username: emrearabacioglu
    Password: 
    Login Succeeded
    
    [ec2-user@ip-172-31-21-191 ~]$ docker pull emrearabacioglu/demo-image:v1
    Status: Downloaded newer image for emrearabacioglu/demo-image:v1
    
    [ec2-user@ip-172-31-21-191 ~]$ docker images
    REPOSITORY                   TAG       IMAGE ID       CREATED          SIZE
    emrearabacioglu/demo-image   v1        b393092c883c   12 minutes ago   1.13GB
    
    [ec2-user@ip-172-31-21-191 ~]$ docker run -d -p 3000:3080 emrearabacioglu/demo-image:v1
    59c32091ca9035ff846218d881903f0901f3cfaebf9b0d95ebb28888ba1670b9
    
    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS         PORTS                                         NAMES
    59c32091ca90   emrearabacioglu/demo-image:v1   "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds   0.0.0.0:3000->3080/tcp, :::3000->3080/tcp   sharp_goldberg

####Security Group Configuration

 Opened firewall to access web app from browser

 <img width="1664" height="271" alt="image" src="https://github.com/user-attachments/assets/61cbbb66-02c7-447e-8ad6-0299b45b6098" />
 <img width="1911" height="545" alt="image" src="https://github.com/user-attachments/assets/92090a65-6fc0-4e18-8740-6d197d9ea650" />



</details>

******

<details>
<summary>Deploy to EC2 server from Jenkins Pipeline - CI/CD Part 1</summary>
 <br />
 
### Demo 1: Deployed WebApp Container via Jenkins Pipeline on EC2 Instance

#### Overview
* Configured a Jenkins `Multi-Branch Pipeline` to automate application deployment.
* Integrated `sshagent` plugin in Jenkins to securely access the AWS EC2 instance.
* Executed remote Docker commands on the EC2 instance via SSH to pull and run the application container.
* Successfully deployed the `emrearabacioglu/demo-app:1.1.1-10` image and exposed it on port `3080`.

#### Execution Logs

    [Pipeline] sshagent
    [ssh-agent] Using credentials ec2-user
    [ssh-agent] Started.
    [Pipeline] {
    [Pipeline] sh
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 docker run -p 3080:8080 -d emrearabacioglu/demo-app:1.1.1-10
    Unable to find image 'emrearabacioglu/demo-app:1.1.1-10' locally
    Status: Downloaded newer image for emrearabacioglu/demo-app:1.1.1-10
    28479044591ba2e368bb6a1a449b2d937f212a7d058601efe047d5519c58bbef
    [Pipeline] }
    ...
    Finished: SUCCESS

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    28479044591b   emrearabacioglu/demo-app:1.1.1-10   "/bin/sh -c 'java -j…"   38 seconds ago   Up 37 seconds   0.0.0.0:3080->8080/tcp, :::3080->8080/tcp   sweet_feynman

<img width="788" height="207" alt="image" src="https://github.com/user-attachments/assets/78dc0ff3-a153-443a-b78c-eca206dc4dcb" />

---

### Demo 2: Deployed Java Maven App via Jenkins Shared Library

#### Overview
* Implemented a `Jenkins Shared Library` (`jenkins-shared-library@master`) to modularize pipeline functions (buildJar, buildImage, dockerLogin, dockerPush).
* Compiled and packaged the Java application locally on the Jenkins server using Maven (`mvn package`).
* Built a new Docker image (`jma-3.0`) and successfully pushed it to DockerHub.
* Deployed the freshly built artifact to the EC2 instance, exposing the service on port `8080`.

#### Execution Logs

    [Pipeline] echo
    building application jar...
    [Pipeline] sh
    + mvn package
    ...
    [INFO] Building jar: /var/jenkins_home/workspace/ultibranch-pipeline_jenkins-jobs/target/java-maven-app-1.1.8.jar
    [INFO] BUILD SUCCESS
    ...
    [Pipeline] echo
    building the docker image...
    [Pipeline] sh
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    ...
    [Pipeline] echo
    pushing the docker image...
    [Pipeline] sh
    + docker push emrearabacioglu/demo-app:jma-3.0
    ...
    jma-3.0: digest: sha256:4b8fad7e4f861372149685a8b1a2fd18e5496c5e5657dcc8fc4d61250b5af05b size: 1159
    ...
    [Pipeline] echo
    deploying docker image to EC2...
    [Pipeline] sh
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 docker run -p 8080:8080 -d emrearabacioglu/demo-app:jma-3.0
    Status: Downloaded newer image for emrearabacioglu/demo-app:jma-3.0
    27b02fffdd94d506571f4c9185c2faa46b7f790c668153bb04b74a714196eaeb
    ...
    Finished: SUCCESS

    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                              COMMAND                  CREATED         STATUS          PORTS                                       NAMES
    27b02fffdd94   emrearabacioglu/demo-app:jma-3.0    "/bin/sh -c 'java -j…"   7 minutes ago   Up 40 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   friendly_hamilton
    28479044591b   emrearabacioglu/demo-app:1.1.1-10   "/bin/sh -c 'java -j…"   6 hours ago     Up 6 hours      0.0.0.0:3080->8080/tcp, :::3080->8080/tcp   sweet_feynman

<img width="883" height="212" alt="image" src="https://github.com/user-attachments/assets/804510fb-86b4-4c6a-b293-a8791a4452b7" />

---

</details>

******

<details>
<summary>Deploy to EC2 server from Jenkins Pipeline - CI/CD Part 2</summary>
 <br />
 
 ### Demo Executed: Deploy Java Maven App via Jenkins Pipeline on EC2 Instance using Docker Compose

#### Overview
Engineered and executed a continuous deployment pipeline to build, containerize, and orchestrate a multi-service architecture on an AWS EC2 instance. Abstracted the deployment logic into a remote shell script (`server-cmds.sh`) and utilized Docker Compose to synchronously provision the Java application and its associated PostgreSQL database.

Jenkinsfile:

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
docker-compose file: 

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

bash script: 

```bash
#!/usr/bin/env groovy

export IMAGE=$1

docker-compose -f docker-compose.yaml up --detach

echo "success"
```

#### Execution Logs & Artifacts

Compiled and packaged the application artifact locally on the Jenkins agent:

    [Pipeline] sh
    + mvn package
    [INFO] Scanning for projects...
    ...
    [INFO] Building jar: /var/jenkins_home/workspace/ultibranch-pipeline_jenkins-jobs/target/java-maven-app-1.1.8.jar
    [INFO] BUILD SUCCESS
    [INFO] Total time:  5.723 s

Built and pushed the application Docker image to the remote registry:

    [Pipeline] sh
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    ...
    [Pipeline] sh
    + docker push emrearabacioglu/demo-app:jma-3.0
    ...
    jma-3.0: digest: sha256:92fb82f7fbe3673c80b8b5bb6a870e266f11e7919d4bf2618ed760e4f1d2ff59 size: 1159

Securely transferred configuration files to the target EC2 environment and triggered the remote deployment script:

    [Pipeline] sh
    + scp server-cmds.sh ec2-user@3.125.50.166:/home/ec2-user
    [Pipeline] sh
    + scp docker-compose.yaml ec2-user@3.125.50.166:/home/ec2-user
    [Pipeline] sh
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 bash ./server-cmds.sh emrearabacioglu/demo-app:jma-3.0

Orchestrated the multi-container environment (Java App + Postgres) via Docker Compose:
     Network ec2-user_default Creating 
     Network ec2-user_default Created 
     Container ec2-user-postgres-1 Creating 
     Container ec2-user-java-maven-app-1 Creating 
     Container ec2-user-java-maven-app-1 Created 
     Container ec2-user-postgres-1 Created 
     Container ec2-user-java-maven-app-1 Starting 
     Container ec2-user-postgres-1 Starting 
     Container ec2-user-java-maven-app-1 Started 
     Container ec2-user-postgres-1 Started 
    success
<img width="899" height="220" alt="image" src="https://github.com/user-attachments/assets/79e4c947-ec71-4918-a989-739a326fd7eb" />

```bash
[ec2-user@ip-172-31-21-191 ~]$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED          STATUS          PORTS                                       NAMES
b40cea0f15dd   emrearabacioglu/demo-app:jma-3.0   "/bin/sh -c 'java -j…"   20 seconds ago   Up 18 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
020d64f33101   postgres:15                        "docker-entrypoint.s…"   20 seconds ago   Up 18 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
```

 
</details>

******

<details>
<summary>Deploy to EC2 server from Jenkins Pipeline - CI/CD Part 3</summary>
 <br />
 
### Demo Executed: Automated Dynamic Versioning & Multi-Container Deployment to AWS EC2

#### Overview
Engineered an end-to-end CI/CD pipeline featuring automated dynamic versioning. Configured the Jenkinsfile to utilize Maven plugins to increment the application patch version automatically during the build process. The pipeline seamlessly builds the newly versioned artifact, constructs and pushes the Docker image to the registry, and orchestrates a multi-container deployment (Java App + PostgreSQL) on an AWS EC2 instance using Docker Compose. Finally, the pipeline commits the version bump back to the source code repository to maintain state consistency.

#### Execution Logs & Artifacts

Jenkinsfile: 
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

Dynamically incremented the application version via Maven Build Helper:

    [Pipeline] sh
    + mvn build-helper:parse-version versions:set -DnewVersion=${parsedVersion.majorVersion}.${parsedVersion.minorVersion}.${parsedVersion.nextIncrementalVersion} versions:commit
    ...
    [INFO] Processing change of com.example:java-maven-app:1.1.8 -> 1.1.9
    [INFO]     Updating project com.example:java-maven-app
    [INFO]         from version 1.1.8 to 1.1.9

Built and pushed the dynamically tagged Docker image:

    [Pipeline] sh
    + docker build -t emrearabacioglu/demo-app:1.1.9-12 .
    ...
    [Pipeline] sh
    + docker push emrearabacioglu/demo-app:1.1.9-12
    ...
    1.1.9-12: digest: sha256:915a34770f02767d81762efd3bd92538db2e68abceffcd27210db69475995817 size: 1159

Executed remote deployment utilizing Docker Compose on the EC2 host:

    [Pipeline] sh
    + ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.9-12
    ...
     Image emrearabacioglu/demo-app:1.1.9-12 Pulled 
     Container ec2-user-java-maven-app-1 Recreate 
     Container ec2-user-java-maven-app-1 Recreated 
     Container ec2-user-java-maven-app-1 Starting 
     Container ec2-user-postgres-1 Starting 
     Container ec2-user-postgres-1 Started 
     Container ec2-user-java-maven-app-1 Started 
    success

Committed and pushed the updated `pom.xml` back to the GitHub repository:

    [Pipeline] sh
    + git commit -m version bump
    [detached HEAD 034949a] version bump
     8 files changed, 25 insertions(+), 28 deletions(-)
    [Pipeline] sh
    + git push origin HEAD:jenkins-jobs
    To https://github.com/emrearabacioglu/java-maven-app.git
       f1fe8e6..034949a  HEAD -> jenkins-jobs

<img width="1184" height="265" alt="image" src="https://github.com/user-attachments/assets/0b5cf21a-dc6c-42e1-bf26-a424006f8c97" />

Verified active containers on the EC2 server:
```bash
    [ec2-user@ip-172-31-21-191 ~]$ docker ps
    CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    42d798c26a0e   emrearabacioglu/demo-app:1.1.9-12   "/bin/sh -c 'java -j…"   36 seconds ago   Up 34 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
    020d64f33101   postgres:15                         "docker-entrypoint.s…"   24 hours ago     Up 34 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
```

 
</details>

******

<details>
<summary>ECR - Elastic Container Registry</summary>
 <br />
 
 ### Demo Executed: AWS ECR Private Registry Integration & Docker Image Deployment

#### Overview
Demonstrated the end-to-end workflow of securely publishing local Docker containers to a private Amazon Elastic Container Registry (ECR). The process entailed provisioning the local AWS CLI environment, establishing an authenticated session between the local Docker client and AWS via IAM credentials, building multiple iterations (`1.0` and `1.1`) of a Node.js application image, and successfully pushing the tagged artifacts to the remote AWS repository.

#### Execution Logs & Artifacts

Configured the AWS CLI environment and successfully authenticated the Docker client with the private ECR registry:
```bash
    root@PC:/mnt/c/Users/emrea# aws configure
    AWS Access Key ID [****************6472]: ******
    AWS Secret Access Key [****************VPGR]: ******
    Default region name [eu-central-1]: eu-central-1
    Default output format [json]: json
    
    root@PC:/mnt/c/Users/emrea# aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded
```
Built the initial Node.js application image (`1.0`), applied the target ECR repository tag, and pushed the artifact:
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.0 .
    [+] Building 1.3s (11/11) FINISHED
    ...
    root@PC:/mnt/c/Users/emrea# docker tag my-app:1.0 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    
    root@PC:/mnt/c/Users/emrea# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.0
    The push refers to repository [731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app]
    9cc1f72199aa: Pushed
    ...
    1.0: digest: sha256:6864de50df6c69649d7fad5dbeab0c774ba73873004dfd7d925a9bd831892474 size: 856
```
Compiled a subsequent version (`1.1`), updated the corresponding ECR tag, and pushed the new iteration:
```bash
    root@PC:/mnt/c/Users/emrea/js-app# docker build -t my-app:1.1 .
    [+] Building 14.4s (11/11) FINISHED
    ...
    root@PC:/mnt/c/Users/emrea/js-app# docker tag my-app:1.1 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    
    root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app:1.1
    The push refers to repository [731872836472.dkr.ecr.eu-central-1.amazonaws.com/my-app]
    cba6f0f7f514: Pushed
    fb899bcb8294: Pushed
    ...
    1.1: digest: sha256:b66fee87f8f9fd58d93f7b97329648f34b2957975fb0f00e74af64be5c1aab20 size: 856
```
<img width="1631" height="624" alt="image" src="https://github.com/user-attachments/assets/4c8b9763-6c25-423c-b4bb-a2d74dfffbbb" />



 
</details>

******

<details>
<summary>Introduction to AWS CLI - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Introduction to AWS CLI - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>AWS & Terraform Preview</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Container Services on AWS Preview</summary>
 <br />
 
 **content will be here**
 
</details>










