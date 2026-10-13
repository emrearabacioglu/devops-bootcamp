# Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline)

**Technologies:** Jenkins, Docker, Linux, Git, Java, Maven

CI for the Java Maven app in `java-maven-app/`: Jenkins builds the jar, builds a Docker image and pushes it to my private Docker Hub repo. I did this with three job types: Freestyle, Pipeline and Multibranch Pipeline.

## Summary
1. Prepared Jenkins: installed Maven (`maven-3.9`) under *Manage Jenkins → Tools*, made Docker available inside the Jenkins container (see `01-install-jenkins-on-digitalocean`) and created the credentials `github-credentials` (Git repo) and `docker-hub-repo` (Docker Hub).
2. **Freestyle job:** Git repo + Maven step `package`, then an "Execute shell" step that runs `docker build`, `docker login` and `docker push emrearabacioglu/demo-app:jma-1.1`. I also pushed the image to a Docker repo on Nexus (`167.172.185.199:8083`). For that I added it to `insecure-registries` in `/etc/docker/daemon.json` on the Jenkins server and restarted Docker.
3. **Pipeline job (first version):** `other-jenkinsfiles/simple-pipeline.Jenkinsfile` has three stages (build, test, Deploy) that only print messages. The Pipeline job read it from my GitHub repo (`jenkins-jobs` branch).
4. **Pipeline job (full version):** `java-maven-app/Jenkinsfile` uses the `maven-3.9` tool and loads `java-maven-app/script.groovy` with `load "script.groovy"`. The functions there:
   - `buildJar()` runs `mvn package`
   - `buildImage()` runs `docker build`, `docker login` and `docker push emrearabacioglu/demo-app:jma-2.0` with the `docker-hub-repo` credentials (`withCredentials`)
   - `deployApp()` only prints a message for now
5. **Multibranch pipeline:** `other-jenkinsfiles/multibranch.Jenkinsfile` runs the `test` stage for every branch, and the `build` and deploy stages only when `BRANCH_NAME == "master"`.

The image is built with `java-maven-app/Dockerfile`.

## Result
Pipeline job with `java-maven-app/Jenkinsfile`: the jar is built and the `jma-2.0` image is pushed to Docker Hub:
```
[Pipeline] { (build jar)
...
+ mvn package
...
[INFO] Building jar: /var/jenkins_home/workspace/my-pipeline/target/java-maven-app-1.1.8.jar
...
[INFO] BUILD SUCCESS
...
[Pipeline] { (build image)
...
+ docker build -t emrearabacioglu/demo-app:jma-2.0 .
...
+ docker login -u emrearabacioglu --password-stdin
Login Succeeded
...
+ docker push emrearabacioglu/demo-app:jma-2.0
...
jma-2.0: digest: sha256:fa5646f916af1851effcbdd4ea210fe8acdf62af2ebd93847c27ec85ca59ebbe size: 1159
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
