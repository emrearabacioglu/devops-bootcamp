# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline)

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
