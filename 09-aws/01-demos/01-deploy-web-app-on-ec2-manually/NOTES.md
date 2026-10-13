# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy Web Application on EC2 Instance (manually)

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
