# CD - Deploy Application from Jenkins Pipeline on EC2 Instance (automatically with docker-compose)

**Technologies:** AWS, Jenkins, Docker, Linux, Git, Java, Maven, Docker Hub

I replaced the `docker run` deploy step with Docker Compose, so my app and a PostgreSQL container start together on the EC2 instance.

## Summary
- Installed Docker Compose on the EC2 instance.
- `java-maven-app/docker-compose.yaml` runs my app image and a `postgres:15` container. The app image name comes from the `IMAGE` variable.
- `java-maven-app/server-cmds.sh` has the commands that run on the server (`export IMAGE=$1` and `docker-compose -f docker-compose.yaml up --detach`), so the Jenkinsfile stays short.
- `java-maven-app/Jenkinsfile` builds the jar and pushes the image `emrearabacioglu/demo-app:jma-3.0` with my [jenkins-shared-library](https://github.com/emrearabacioglu/jenkins-shared-library), same as the previous demo.
- The deploy stage copies `server-cmds.sh` and `docker-compose.yaml` to the server with `scp` and runs the script over SSH with the image name as argument (credential `ec2-server-key`):

```groovy
sshagent(['ec2-server-key']) {
    sh "scp server-cmds.sh ${ec2Instance}:/home/ec2-user"
    sh "scp docker-compose.yaml ${ec2Instance}:/home/ec2-user"
    sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
}
```

## Result
Jenkins copied the files, ran the script, and Docker Compose started both containers:
```
+ scp server-cmds.sh ec2-user@3.125.50.166:/home/ec2-user
+ scp docker-compose.yaml ec2-user@3.125.50.166:/home/ec2-user
+ ssh -o StrictHostKeyChecking=no ec2-user@3.125.50.166 bash ./server-cmds.sh emrearabacioglu/demo-app:jma-3.0
...
 Container ec2-user-java-maven-app-1 Started
 Container ec2-user-postgres-1 Started
success

[ec2-user@ip-172-31-21-191 ~]$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED          STATUS          PORTS                                       NAMES
b40cea0f15dd   emrearabacioglu/demo-app:jma-3.0   "/bin/sh -c 'java -j…"   20 seconds ago   Up 18 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
020d64f33101   postgres:15                        "docker-entrypoint.s…"   20 seconds ago   Up 18 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
