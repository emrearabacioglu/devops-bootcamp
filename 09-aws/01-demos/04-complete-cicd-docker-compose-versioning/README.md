# Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning)

**Technologies:** AWS, Jenkins, Docker, Linux, Git, Java, Maven, Docker Hub

This is the final pipeline of the module. Every run raises the app version, builds and pushes a new image, deploys it to EC2 with Docker Compose and commits the new version back to GitHub.

## Summary
`java-maven-app/Jenkinsfile` has five stages:
1. **increment version** (CI): Maven raises the patch version in `pom.xml`. The image tag becomes `<version>-<BUILD_NUMBER>`.
2. **build app** (CI): `buildJar()` from my [jenkins-shared-library](https://github.com/emrearabacioglu/jenkins-shared-library).
3. **build image** (CI): builds the image with `java-maven-app/Dockerfile` and pushes it to Docker Hub with the new tag.
4. **deploy** (CD): copies `docker-compose.yaml` and `server-cmds.sh` to the EC2 instance with `scp` and runs the script over SSH (credential `ec2-server-key`). Both files are the same as in the previous demo.
5. **commit version update** (CD): pushes the changed `pom.xml` to the `jenkins-jobs` branch of my java-maven-app repo, using the `github-credentials` credential.

## Result
The version went from 1.1.8 to 1.1.9, the image `1.1.9-12` was deployed and the version bump was pushed to GitHub:
```
[INFO] Processing change of com.example:java-maven-app:1.1.8 -> 1.1.9
...
+ docker push emrearabacioglu/demo-app:1.1.9-12
...
 Image emrearabacioglu/demo-app:1.1.9-12 Pulled
 Container ec2-user-java-maven-app-1 Recreated
...
+ git push origin HEAD:jenkins-jobs
To https://github.com/emrearabacioglu/java-maven-app.git
   f1fe8e6..034949a  HEAD -> jenkins-jobs

[ec2-user@ip-172-31-21-191 ~]$ docker ps
CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
42d798c26a0e   emrearabacioglu/demo-app:1.1.9-12   "/bin/sh -c 'java -j…"   36 seconds ago   Up 34 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   ec2-user-java-maven-app-1
020d64f33101   postgres:15                         "docker-entrypoint.s…"   24 hours ago     Up 34 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
