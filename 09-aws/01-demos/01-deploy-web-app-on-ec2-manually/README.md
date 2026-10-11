# Deploy Web Application on EC2 Instance (manually)

**Technologies:** AWS, Docker, Linux

I created an EC2 instance on AWS, installed Docker on it and ran my app image from my private Docker Hub repo.

## Summary
1. Created an Amazon Linux 2023 instance in the AWS console and downloaded the key pair `docker-server.pem`.
2. Connected to the instance with SSH using the key.
3. Installed and started Docker, then added `ec2-user` to the `docker` group so I can run Docker without `sudo`.
4. Logged in to Docker Hub, pulled `emrearabacioglu/demo-image:v1` and started it with host port 3000 mapped to container port 3080.
5. Added an inbound rule to the security group so I can open the app from the browser.

## Run
```bash
chmod 400 docker-server.pem
ssh -i docker-server.pem ec2-user@<public-ip>

sudo yum install docker
sudo service docker start
sudo usermod -aG docker $USER

docker login
docker pull emrearabacioglu/demo-image:v1
docker run -d -p 3000:3080 emrearabacioglu/demo-image:v1
```

## Result
The image is pulled from my private repo and the container is running on the EC2 instance:
```
[ec2-user@ip-172-31-21-191 ~]$ docker pull emrearabacioglu/demo-image:v1
Status: Downloaded newer image for emrearabacioglu/demo-image:v1

[ec2-user@ip-172-31-21-191 ~]$ docker run -d -p 3000:3080 emrearabacioglu/demo-image:v1

[ec2-user@ip-172-31-21-191 ~]$ docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS         PORTS                                         NAMES
59c32091ca90   emrearabacioglu/demo-image:v1   "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds   0.0.0.0:3000->3080/tcp, :::3000->3080/tcp   sharp_goldberg
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
