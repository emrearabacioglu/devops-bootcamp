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
 
 **content will be here**
 
</details>

******

<details>
<summary>Deploy to EC2 server from Jenkins Pipeline - CI/CD Part 3</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>ECR - Elastic Container Registry</summary>
 <br />
 
 **content will be here**
 
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










