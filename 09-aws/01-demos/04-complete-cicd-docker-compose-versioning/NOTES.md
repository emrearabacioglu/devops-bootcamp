# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning)

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
