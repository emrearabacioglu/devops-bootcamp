# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## CD – Deploy Application from Jenkins Pipeline on EC2 Instance (automatically with docker-compose)

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
