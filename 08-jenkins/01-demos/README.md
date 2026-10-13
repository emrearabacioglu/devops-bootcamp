# Module 8 – Build Automation & CI/CD with Jenkins

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline) | Docker inside the Jenkins container, freestyle jobs pushing to Docker Hub and Nexus, first Pipeline job, full pipeline with `script.groovy` |
| 2 | Create a Jenkins Shared Library | Build and Docker steps moved to a shared library repo with a `Docker` Groovy class |
| 3 | Configure Webhook to trigger CI Pipeline automatically on every change | Not written yet (placeholder) |
| 4 | Dynamically Increment Application version in Jenkins Pipeline | Version bump in `pom.xml` → build → push `<version>-<build number>` image → commit version back to Git |

## Takeaways

- **Docker inside the Jenkins container:** run Jenkins with `-v /var/run/docker.sock:/var/run/docker.sock`, install Docker inside the container as root (`docker exec -it -u 0 <id> bash` + the get.docker.com script), then `chmod 666 /var/run/docker.sock` so the `jenkins` user can use it.
- **Docker restart on the host:** after `systemctl restart docker` the Jenkins container has to be started again (`docker start <id>`). Check the socket permissions with `ls -l /var/run/docker.sock`.
- **Insecure Nexus registry:** add `"insecure-registries":["167.172.185.199:8083"]` to `/etc/docker/daemon.json` and restart Docker. `docker login`, tag and push all use `<ip>:<port>`.
- **docker login in a job:** `echo $PASSWORD | docker login -u $USERNAME --password-stdin`. Docker warns that the credentials are stored unencrypted in `/var/jenkins_home/.docker/config.json`.
- **Credentials in a pipeline:** `withCredentials([usernamePassword(credentialsId: ..., passwordVariable: 'PASS', usernameVariable: 'USER')])`. The password shows up as `****` in the log.
- **Jenkinsfile basics:** `pipeline` → `agent any` → `stages` → `stage('...')` → `steps`. `tools { maven 'maven-3.9' }` makes `mvn` available in the stages.
- **External Groovy script:** load it in an `init` stage with `gv = load "script.groovy"` (`def gv` above `pipeline`). The script must end with `return this`.
- **Shared library:** loaded per project in the Jenkinsfile with `library identifier: 'jenkins-shared-library@master', retriever: modernSCM(...)`. Each step file has a `call()` function. The `Docker` class `implements Serializable` and gets `this` from the step, so it calls `script.sh`, `script.echo`, `script.withCredentials`.
- **Version bump:** `mvn build-helper:parse-version versions:set -DnewVersion=...nextIncrementalVersion versions:commit`, then read the version with `readFile('pom.xml') =~ '<version>(.+)</version>'`. Image tag = `<version>-$BUILD_NUMBER`.
- **Changing jar name:** the Dockerfile uses `java-maven-app-*.jar`, so it works with any version.
- **Commit from Jenkins:** set `git config user.email`/`user.name`, put the credentials in the remote URL, and push with `git push origin HEAD:<branch>` because Jenkins checks out a detached HEAD.

******

<details>
<summary>Demo Project: Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline)</summary>
 <br />

### Demo Executed: Docker in Jenkins (freestyle jobs, Docker Hub and Nexus)

#### Docker Socket and Permissions
Started Jenkins with the host's `docker.sock` mounted. Then installed Docker inside the container as root and gave everyone read/write on the socket so the `jenkins` user can run Docker commands:
```bash
    [Host Terminal Execution]
    root@ubuntu-jenkins:~# docker run -p 8080:8080 -p 50000:50000 -d \
    > -v jenkins_home:/var/jenkins_home \
    > -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts
    4b8376846d81ec0d1e9ff44006d01094fca9bc0006e1fcb8f4bf0312ae1781fe
    
    root@ubuntu-jenkins:~# docker exec -it -u 0 4b8376846d81 bash
    root@4b8376846d81:/# curl https://get.docker.com/ > dockerinstall && chmod 777 dockerinstall && ./dockerinstall
    ...
    root@4b8376846d81:/# chmod 666 /var/run/docker.sock
    root@4b8376846d81:/# ls -l /var/run/docker.sock
    srw-rw-rw- 1 root 112 0 Apr  4 11:02 /var/run/docker.sock
```
#### Build and Push to Docker Hub
A freestyle job pulls the code, builds the Java app with Maven, builds the Docker image and pushes it to Docker Hub using stored credentials.

Execute shell step of the job:
```bash
    [Jenkins Job Execute Shell]
    docker build -t emrearabacioglu/demo-app:jma-1.1 .
    echo $PASSWORD | docker login -u $USERNAME --password-stdin
    docker push emrearabacioglu/demo-app:jma-1.1
```
Build log, Maven build and the push to Docker Hub:
```
    [Jenkins Job Build Logs]
    [java-maven-build] $ /var/jenkins_home/tools/hudson.tasks.Maven_MavenInstallation/maven-3.9/bin/mvn package
    ...
    [INFO] BUILD SUCCESS
    [INFO] Total time:  5.003 s
    [INFO] Finished at: 2026-04-05T11:04:29Z
    ...
    + docker build -t emrearabacioglu/demo-app:jma-1.1 .
    #9 naming to docker.io/emrearabacioglu/demo-app:jma-1.1 done
    #9 DONE 0.2s
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    + docker push emrearabacioglu/demo-app:jma-1.1
    The push refers to repository [docker.io/emrearabacioglu/demo-app]
    ...
    140c1eb7b411: Pushed
    jma-1.1: digest: sha256:e954febd9ba2113cb145af9c7fe77ade121537c6edc4b5cac4cdc16192a86482 size: 1159
    Finished: SUCCESS
```
Images inside the Jenkins container after two builds (`jma-1.0`, `jma-1.1`):
```bash
    [Host Terminal Verification]
    jenkins@4b8376846d81:/$ docker images
    IMAGE                              ID             DISK USAGE   CONTENT SIZE   EXTRA
    emrearabacioglu/demo-app:jma-1.0   17289c915a81        320MB             0B
    emrearabacioglu/demo-app:jma-1.1   b922e645eadc        320MB             0B
```

<img width="2996" height="664" alt="image" src="https://github.com/user-attachments/assets/781e5ff7-fa26-475e-8a3c-31bab56939c3" />

#### Allow the Nexus Registry over HTTP
Added the Nexus Docker repo as an insecure registry in the host's Docker daemon config and restarted Docker. Then started the Jenkins container again and checked the socket permissions:
```bash
    [Host Terminal Execution]
    root@ubuntu-jenkins:~# cat /etc/docker/daemon.json
    {
            "insecure-registries":["167.172.185.199:8083"]
    }
    root@ubuntu-jenkins:~# systemctl restart docker
    ...
    root@ubuntu-jenkins:~# docker start 4b8376846d81
    4b8376846d81
    root@ubuntu-jenkins:~# docker exec -it -u 0 4b8376846d81 bash
    root@4b8376846d81:/# ls -l /var/run/docker.sock
    srw-rw-rw- 1 root 112 0 Apr  4 11:02 /var/run/docker.sock
```
#### Build and Push to Nexus
Same job, now tagging and pushing the image to the Nexus registry (`167.172.185.199:8083`).

Execute shell step of the job:
```bash
    [Jenkins Job Execute Shell]
    docker build -t 167.172.185.199:8083/java-maven-app:1.1 .
    echo $PASSWORD | docker login -u $USERNAME --password-stdin 167.172.185.199:8083
    docker push 167.172.185.199:8083/java-maven-app:1.1
```
Build log with the login and push to Nexus:
```
    [Jenkins Job Build Logs]
    + docker build -t 167.172.185.199:8083/java-maven-app:1.1 .
    ...
    + docker login -u docker-repo --password-stdin 167.172.185.199:8083
    WARNING! Your credentials are stored unencrypted in '/var/jenkins_home/.docker/config.json'.
    Login Succeeded
    + docker push 167.172.185.199:8083/java-maven-app:1.1
    The push refers to repository [167.172.185.199:8083/java-maven-app]
    5f70bf18a086: Pushed
    1fbc58c1783a: Pushed
    3d146006478f: Pushed
    1.1: digest: sha256:649ca0de5c3aae601c71778e32e91d0946a44bf1a9c1aa31bb27036f703d7cf3 size: 1159
    Finished: SUCCESS
```
<img width="2372" height="788" alt="image" src="https://github.com/user-attachments/assets/08d413eb-68bd-4e51-a2f4-f952b8c48bdb" />

### Demo Executed: First Pipeline job

#### Jenkinsfile
Added a simple declarative `Jenkinsfile` to the Git repo with three stages (build, test, deploy) that only print messages:
```groovy
    pipeline{
        agent any
        stages{
            stage("build") {
                steps {
                    echo 'building the application...'
                }
            }
            stage("test") {
                steps {
                    echo 'Testing the application...'
                }
            }
            stage("Deploy") {
                steps {
                    echo 'Deploying the application...'
                }
            }
        }
    }
```
#### Pipeline Job Run
Created a Pipeline job in Jenkins that reads the `Jenkinsfile` from the GitHub repo. Jenkins checked out the `jenkins-jobs` branch and ran the three stages:
```
    Started by user emre
    Obtained Jenkinsfile from git https://github.com/emrearabacioglu/java-maven-app.git
    ...
    Running on Jenkins in /var/jenkins_home/workspace/my-pipeline
    ...
    using credential github-credentials
    Cloning repository https://github.com/emrearabacioglu/java-maven-app.git
    ...
    Checking out Revision 80b3d98f6d6378f14c67581b5f84384185b43576 (refs/remotes/origin/jenkins-jobs)
    ...
    Commit message: "Update Jenkinsfile"
    ...
    [Pipeline] { (build)
    ...
    building the application...
    ...
    [Pipeline] { (test)
    ...
    Testing the application...
    ...
    [Pipeline] { (Deploy)
    ...
    Deploying the application...
    ...
    Finished: SUCCESS
```
#### Command Summary
* `pipeline {}`: root block of a declarative pipeline.
* `agent any`: run the pipeline (or a stage) on any available node.
* `stage('...') {}`: one step of the process, e.g. build, test, deploy.
* `steps {}`: the commands that run inside a stage.
* `echo '...'`: prints a message to the console output.

### Demo Executed: Full pipeline with `script.groovy`

#### Jenkinsfile and script.groovy
A declarative pipeline with Maven as the build tool. The actual steps are in a separate `script.groovy` file, which is loaded in the `init` stage.

`Jenkinsfile`:
```groovy
    def gv 

    pipeline{
        agent any
        tools{
            maven 'maven-3.9'
        }
        stages{
            stage("init"){
                steps{
                    script{
                        gv = load "script.groovy"
                    }
                }
            }
            stage("build jar"){
                steps{
                    script{
                        gv.buildJar()
                    }
                }
            }
            stage("build image"){
                steps{
                    script{
                        gv.buildImage()
                    }
                }
            }
            stage("deploy"){
                steps{
                    script{
                        gv.deployApp()
                    }
                }
            }
        }
    }
```
`script.groovy`:
```groovy
    def buildJar(){
        echo 'building the application..'
        sh 'mvn package'
    }

    def buildImage(){
        echo"building the docker image..."
        withCredentials([usernamePassword(credentialsId: 'docker-hub-repo', passwordVariable:'PASS', usernameVariable: 'USER')]){
        sh 'docker build -t emrearabacioglu/demo-app:jma-2.0 .'
        sh 'echo $PASS | docker login -u $USER --password-stdin'
        sh 'docker push emrearabacioglu/demo-app:jma-2.0'
        }
    }

    def deployApp(){
        echo 'deployin the application...'
    }

    return this
```
#### Build Jar
The `buildJar` function runs `mvn package`. Tests passed and the jar was created in the workspace:
```text
    [Pipeline] { (build jar)
    ...
    building the application..
    ...
    + mvn package
    [INFO] Scanning for projects...
    [INFO] ---------------------< com.example:java-maven-app >---------------------
    [INFO] Building java-maven-app 1.1.8
    ...
    [INFO] --- surefire:3.5.4:test (default-test) @ java-maven-app ---
    [INFO] Running AppTest
    [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.117 s -- in AppTest
    ...
    [INFO] Building jar: /var/jenkins_home/workspace/my-pipeline/target/java-maven-app-1.1.8.jar
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD SUCCESS
    [INFO] Total time:  5.216 s
    [INFO] Finished at: 2026-04-06T16:12:02Z
```
#### Build and Push Image
The `buildImage` function builds the image and pushes `jma-2.0` to Docker Hub. Docker Hub credentials come from `withCredentials`, so the password is masked in the log:
```text
    [Pipeline] { (build image)
    ...
    building the docker image...
    [Pipeline] withCredentials
    Masking supported pattern matches of $PASS
    ...
    + docker build -t emrearabacioglu/demo-app:jma-2.0 .
    ...
    #9 writing image sha256:8f23d27432b0b31924fb939992d46b840db46de0ef4858009c6bb0993716cb37 done
    #9 naming to docker.io/emrearabacioglu/demo-app:jma-2.0 done
    ...
    + echo ****
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    ...
    + docker push emrearabacioglu/demo-app:jma-2.0
    The push refers to repository [docker.io/emrearabacioglu/demo-app]
    ...
    d6c3c2dd4b22: Pushed
    jma-2.0: digest: sha256:fa5646f916af1851effcbdd4ea210fe8acdf62af2ebd93847c27ec85ca59ebbe size: 1159
```
<img width="2980" height="921" alt="image" src="https://github.com/user-attachments/assets/bda71adb-0452-4d14-bd91-cb8a8e05a44a" />

<img width="1891" height="617" alt="image" src="https://github.com/user-attachments/assets/df311cc4-4ccf-438f-8aac-2d5f426312fc" />

</details>

******

<details>
<summary>Demo Project: Create a Jenkins Shared Library</summary>
 <br />

### Demo Executed: Move build and Docker steps to a shared library

#### Files
Moved the build and Docker steps to a separate repo, `jenkins-shared-library`. The Docker logic is in the `com.example.Docker` class, and each pipeline step (`buildJar`, `buildImage`, `dockerLogin`, `dockerPush`) is its own script. The deploy stage still uses `script.groovy`.

`Jenkinsfile`:

    #!/user/bin/env groovy
    library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
        [$class: 'GitSCMSource',
        remote: 'https://github.com/emrearabacioglu/jenkins-shared-library.git', 
        credentialsId: 'github-credentials'])

    def gv 

    pipeline{
        agent any
        tools{
            maven 'maven-3.9'
        }
        stages{
            stage("init"){
                steps{
                    script{
                        gv = load "script.groovy"
                    }
                }
            }
            stage("build jar"){
                steps{
                    script{
                        buildJar()
                    }
                }
            }
            stage("build and push image"){
                steps{
                    script{
                        buildImage 'emrearabacioglu/demo-app:jma-3.0'
                        dockerLogin()
                        dockerPush 'emrearabacioglu/demo-app:jma-3.0'
                        
                    }
                }
            }
            stage("deploy"){
                steps{
                    script{
                        gv.deployApp()
                    }
                }
            }
        }
    }

`script.groovy`:

    def deployApp() {
        echo 'deploying the application...'
    }
    return this

`Docker.groovy` (class):

    #!/user/bin/env groovy
    package com.example

    class Docker implements Serializable {
        def script

        Docker(script) {
            this.script = script
        }

        def buildDockerImage(String imageName){
            script.echo"building the docker image..."
            script.sh "docker build -t $imageName ."
        }

        def dockerLogin() {
            script.echo"Logging into Docker Repository..."
            script.withCredentials([script.usernamePassword(credentialsId: 'docker-hub-repo', passwordVariable:'PASS', usernameVariable: 'USER')]){
                script.sh "echo '${script.PASS}' | docker login -u '${script.USER}' --password-stdin"
            }
        }

        def dockerPush(String imageName) {
            script.echo"pushing the docker image..."
            script.sh "docker push $imageName"
        }
    }

`buildImage.groovy`:

    #!/user/bin/env groovy
    import com.example.Docker

    def call(String imageName) {
        return new Docker(this).buildDockerImage(imageName)
    }

`buildJar.groovy`:

    #!/user/bin/env groovy
    def call() {
        echo "building the application.. for branch $GIT_BRANCH"
        sh 'mvn package'
    }

`dockerLogin.groovy`:

    #!/user/bin/env groovy
    import com.example.Docker

    def call() {
        return new Docker(this).dockerLogin()
    }

`dockerPush.groovy`:

    #!/user/bin/env groovy
    import com.example.Docker

    def call(String imageName) {
        return new Docker(this).dockerPush(imageName)
    }

#### Loading the Library
The library is loaded from GitHub inside the `Jenkinsfile` with the `library identifier` block:

    [Pipeline] library
    Loading library jenkins-shared-library@master
    Attempting to resolve master from remote references...
     > git fetch --no-tags --force --progress -- https://github.com/emrearabacioglu/jenkins-shared-library.git +refs/heads/*:refs/remotes/origin/* # timeout=10
    Checking out Revision 5d73a3e1ca7d6e3a1f0246abb0c83e847e08ac1d (master)
    Commit message: "Update Docker.groovy"

#### buildJar Step
The `buildJar()` step from the library printed the branch name from `$GIT_BRANCH` and ran the Maven build:

    building the application.. for branch jenkins-shared-lib
    ...
    + mvn package
    [INFO] Scanning for projects...
    [INFO] Building java-maven-app 1.1.0-SNAPSHOT
    ...
    [INFO] Replacing main artifact /var/jenkins_home/workspace/ice-user-auth_jenkins-shared-lib/target/java-maven-app-1.1.0-SNAPSHOT.jar
    [INFO] BUILD SUCCESS
    [INFO] Total time:  2.719 s
    [INFO] Finished at: 2026-04-07T09:33:54Z

#### Build and Push with the Docker Class
`buildImage`, `dockerLogin` and `dockerPush` call the `Docker` class methods with the image name from the `Jenkinsfile`. The image `jma-3.0` was built and pushed:

    building the docker image...
    ...
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    ...
    #9 writing image sha256:1ea4dc8739a586e103b99d529dd9447cc7ec6436428777b3ecbc104dce5fe57e done
    #9 naming to docker.io/emrearabacioglu/demo-app:jma-3.0 done
    ...
    Logging into Docker Repository...
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    ...
    pushing the docker image...
    ...
    + docker push emrearabacioglu/demo-app:jma-3.0
    The push refers to repository [docker.io/emrearabacioglu/demo-app]
    jma-3.0: digest: sha256:3c815248c19e549f5f3a04844d7bb86614a8de79d2965be158e84003c6aa6c17 size: 1159
    Finished: SUCCESS

</details>

******

<details>
<summary>Demo Project: Configure Webhook to trigger CI Pipeline automatically on every change</summary>
 <br />

 **content will be here**

</details>

******

<details>
<summary>Demo Project: Dynamically Increment Application version in Jenkins Pipeline</summary>
 <br />

### Demo Executed: Version bump, image tag and commit back to Git

#### Files
Each run increases the patch version in `pom.xml`, builds the app, tags the image as `<version>-<build number>`, pushes it, and commits the new `pom.xml` back to the `increment` branch. Git and Jenkins were set to ignore the "version bump" commits so they don't start the pipeline again in a loop.

`Jenkinsfile`:
```
    pipeline{
        agent any
        tools{
            maven 'maven-3.9'
        }
        stages{
            stage("increment version") {
                steps{
                    script{
                        echo 'incrementing the app version...'
                        sh 'mvn build-helper:parse-version versions:set -DnewVersion=\\${parsedVersion.majorVersion}.\\${parsedVersion.minorVersion}.\\${parsedVersion.nextIncrementalVersion} versions:commit'
                        
                        def matcher = readFile('pom.xml') =~ '<version>(.+)</version>'
                        def version = matcher[0][1]
                        env.IMAGE_NAME = "$version-$BUILD_NUMBER"
                    }
                }
            }
            stage("build app") {
                steps {
                    script{
                        echo "building the app..."
                        sh 'mvn clean package'
                    }
                }
            }
            stage("build image") {
                steps {
                    script{
                        echo "Building the docker image..."
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-repo', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh "docker build -t emrearabacioglu/demo-app:$IMAGE_NAME ."
                            sh 'echo $PASS | docker login -u $USER --password-stdin'
                            sh "docker push emrearabacioglu/demo-app:$IMAGE_NAME"
                        }
                    }
                }
            }
            stage("deploy") {
                steps {
                    script{
                        echo "deploying the app..."
                    }
                }
            }
            stage('commit version update') {
                steps{
                    script{
                        withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh 'git config --global user.email "jenkins@example.com" '
                            sh 'git config --global user.name "jenkins" '
                            sh 'git status'
                            sh 'git branch'
                            sh 'git config --list'
                            sh "git remote set-url origin https://${USER}:${PASS}@github.com/emrearabacioglu/java-maven-app.git"
                            sh 'git add .'
                            sh 'git commit -m "version bump"'
                            sh 'git push origin HEAD:increment'
                        }
                    }
                }
            }
        }
    }
```
`Dockerfile`:
```
    FROM amazoncorretto:17-alpine-jdk

    EXPOSE 8080

    COPY ./target/java-maven-app-*.jar /usr/app/
    WORKDIR /usr/app

    CMD java -jar java-maven-app-*.jar
```
#### Version Increment and Build
The Maven Build Helper plugin parsed the version and increased the patch number (1.1.23 → 1.1.24). Then `mvn clean package` built the new jar:
```
    [INFO] Processing change of com.example:java-maven-app:1.1.23 -> 1.1.24
    [INFO]     Updating project com.example:java-maven-app
    [INFO]         from version 1.1.23 to 1.1.24
    ...
    [INFO] Building jar: /var/jenkins_home/workspace/microservice-user-auth_increment/target/java-maven-app-1.1.24.jar
    [INFO] Replacing main artifact /var/jenkins_home/workspace/microservice-user-auth_increment/target/java-maven-app-1.1.24.jar with repackaged archive
    ...
    [INFO] BUILD SUCCESS
    [INFO] Finished at: 2026-04-13T20:42:16Z
```
#### Build and Push Image
The image tag is the version from `pom.xml` plus the Jenkins build number (`1.1.24-32`):
```
    + docker build -t emrearabacioglu/demo-app:1.1.24-32 .
    ...
    #8 writing image sha256:e5e8102b46a523395f59424e2f9fdbf843867a4474cc413796aac81744e4b258 done
    #8 naming to docker.io/emrearabacioglu/demo-app:1.1.24-32 done
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    ...
    + docker push emrearabacioglu/demo-app:1.1.24-32
    The push refers to repository [docker.io/emrearabacioglu/demo-app]
    ...
    3f8d29cb43d2: Pushed
    1.1.24-32: digest: sha256:402cc13596c014025cddc7201158b0bf097ab6badf0238de8697877714c08eda size: 1159
```
#### Commit the Version Back to Git
Jenkins committed the changed `pom.xml` (using the `github-credentials` token) and pushed it from the detached HEAD to the `increment` branch:
```
    + git commit -m version bump
    [detached HEAD 1759cf6] version bump
     1 file changed, 1 insertion(+), 1 deletion(-)
    ...
    + git push origin HEAD:increment
    To https://github.com/emrearabacioglu/java-maven-app.git
       5394116..1759cf6  HEAD -> increment
    ...
    Finished: SUCCESS
```
</details>

******
