# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## CD – Deploy Application from Jenkins Pipeline to EC2 Instance (automatically with docker)

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
