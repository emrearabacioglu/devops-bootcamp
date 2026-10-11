# Dynamically Increment Application version in Jenkins Pipeline

**Technologies:** Jenkins, Docker, GitHub, Git, Java, Maven

Every pipeline run raises the patch version of the Java Maven app, builds a Docker image tagged with the new version and pushes it, then commits the new version back to Git. I used GitHub instead of GitLab.

## Summary
The stages in `java-maven-app/Jenkinsfile`:
1. **increment version:** `mvn build-helper:parse-version versions:set ... versions:commit` raises the patch version in `java-maven-app/pom.xml`. The new version + `BUILD_NUMBER` becomes the image tag (`IMAGE_NAME`, for example `1.1.24-32`).
2. **build app:** `mvn clean package`. `clean` removes the old jar, so there is only one jar in `target/`.
3. **build image:** `docker build` and `docker push emrearabacioglu/demo-app:$IMAGE_NAME` with the `docker-hub-repo` credentials. `java-maven-app/Dockerfile` uses `java-maven-app-*.jar`, so it works for every new version.
4. **deploy:** only prints a message.
5. **commit version update:** Jenkins commits the changed `pom.xml` and pushes it back to GitHub with `git push origin HEAD:increment`, using the `github-credentials`.

Avoid a commit loop: the commit from Jenkins would trigger the pipeline again, so I configured the job to ignore commits made by the Jenkins user.

## Result
Version `1.1.23` → `1.1.24`, image `1.1.24-32` pushed to Docker Hub and the version bump pushed to the `increment` branch:
```
[INFO] Processing change of com.example:java-maven-app:1.1.23 -> 1.1.24
...
[INFO] Building jar: /var/jenkins_home/workspace/microservice-user-auth_increment/target/java-maven-app-1.1.24.jar
...
+ docker push emrearabacioglu/demo-app:1.1.24-32
...
1.1.24-32: digest: sha256:402cc13596c014025cddc7201158b0bf097ab6badf0238de8697877714c08eda size: 1159
...
+ git commit -m version bump
[detached HEAD 1759cf6] version bump
...
+ git push origin HEAD:increment
To https://github.com/emrearabacioglu/java-maven-app.git
   5394116..1759cf6  HEAD -> increment
...
Finished: SUCCESS
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
