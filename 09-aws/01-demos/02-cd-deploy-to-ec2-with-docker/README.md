# CD - Deploy Application from Jenkins Pipeline to EC2 Instance (automatically with docker)

**Technologies:** AWS, Jenkins, Docker, Linux, Git, Java, Maven, Docker Hub

I extended my CI pipeline with a deploy stage. Jenkins connects to the EC2 instance with SSH and starts the newly built image with `docker run`.

## Summary
- Used the EC2 instance with Docker from the previous demo as the deploy server.
- Installed the **SSH Agent** plugin in Jenkins and added the EC2 key as an "SSH Username with private key" credential (`ec2-server-key`, user `ec2-user`).
- Opened port 22 for the Jenkins server IP and port 8080 for the browser in the EC2 security group.
- `java-maven-app/Jenkinsfile` (multibranch pipeline) loads my [jenkins-shared-library](https://github.com/emrearabacioglu/jenkins-shared-library) and has three stages: build the jar (`buildJar`), build and push the image `emrearabacioglu/demo-app:jma-3.0` to Docker Hub (`buildImage`, `dockerLogin`, `dockerPush`), and deploy.
- The deploy stage runs `ssh ... docker run -p 8080:8080 -d emrearabacioglu/demo-app:jma-3.0` on the EC2 instance inside `sshagent(['ec2-server-key'])`.
- `java-maven-app/Dockerfile` builds the image from the jar on `amazoncorretto:17-alpine-jdk`.

Note: `java-maven-app/Jenkinsfile` was reconstructed from my notes and the build logs.

## Result
Jenkins built and pushed the image, then started it on the EC2 instance:
```
+ docker push emrearabacioglu/demo-app:jma-3.0
...
jma-3.0: digest: sha256:4b8fad7e4f861372149685a8b1a2fd18e5496c5e5657dcc8fc4d61250b5af05b size: 1159
deploying docker image to EC2...
+ ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 docker run -p 8080:8080 -d emrearabacioglu/demo-app:jma-3.0
Status: Downloaded newer image for emrearabacioglu/demo-app:jma-3.0
...
Finished: SUCCESS

[ec2-user@ip-172-31-21-191 ~]$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED         STATUS          PORTS                                       NAMES
27b02fffdd94   emrearabacioglu/demo-app:jma-3.0    "/bin/sh -c 'java -j…"   7 minutes ago   Up 40 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   friendly_hamilton
28479044591b   emrearabacioglu/demo-app:1.1.1-10   "/bin/sh -c 'java -j…"   6 hours ago     Up 6 hours      0.0.0.0:3080->8080/tcp, :::3080->8080/tcp   sweet_feynman
```
(The second container is from an earlier run that deployed the existing image `1.1.1-10` on port 3080.)

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
