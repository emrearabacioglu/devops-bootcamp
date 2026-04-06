******

<details>
<summary>Docker in Jenkins</summary>
 <br />
 
### Automated Docker Image Build and Registry Publishing via Jenkins

#### Host System Configuration: Docker-in-Docker & Socket Permissions
Configured the Jenkins container to interact with the host's Docker daemon by mounting the `docker.sock` volume. Resolved socket permission constraints via the host terminal to ensure the Jenkins user could seamlessly execute containerization commands directly from within the container.
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
#### Artifact Build and DockerHub Integration
Designed a Jenkins automated job to fetch source code, compile the Java application, build the Docker image, and securely push it to a public DockerHub repository utilizing stored credentials.
```bash
    [Jenkins Job Execute Shell]
    docker build -t emrearabacioglu/demo-app:jma-1.1 .
    echo $PASSWORD | docker login -u $USERNAME --password-stdin
    docker push emrearabacioglu/demo-app:jma-1.1
```
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
```bash
    [Host Terminal Verification]
    jenkins@4b8376846d81:/$ docker images
    IMAGE                              ID             DISK USAGE   CONTENT SIZE   EXTRA
    emrearabacioglu/demo-app:jma-1.0   17289c915a81        320MB             0B
    emrearabacioglu/demo-app:jma-1.1   b922e645eadc        320MB             0B
```

<img width="2996" height="664" alt="image" src="https://github.com/user-attachments/assets/781e5ff7-fa26-475e-8a3c-31bab56939c3" />

#### Host System Configuration: Private Nexus Registry Bypasses
Configured the host server's Docker daemon to bypass TLS verification for a self-hosted Nexus repository. Re-established container socket permissions following the daemon restart to maintain continuous integration capabilities.
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
#### Nexus Repository Deployment
Successfully executed a Jenkins build sequence to tag and push the compiled artifact directly to the self-hosted, insecure Nexus registry (`167.172.185.199:8083`).
```bash
    [Jenkins Job Execute Shell]
    docker build -t 167.172.185.199:8083/java-maven-app:1.1 .
    echo $PASSWORD | docker login -u $USERNAME --password-stdin 167.172.185.199:8083
    docker push 167.172.185.199:8083/java-maven-app:1.1
```
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

</details>

******

<details>
<summary>Introduction to Pipeline Job</summary>
 <br />
 
### Jenkins Declarative Pipeline Implementation

#### Pipeline as Code Configuration
Engineered a declarative `Jenkinsfile` and integrated it directly into the Git repository. The pipeline is designed with a basic three-tier architecture (Build, Test, Deploy) to demonstrate continuous integration stages as code. 
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
#### Pipeline Job Execution
Configured a Pipeline Job in the Jenkins UI to pull the source code and pipeline definition from the remote GitHub repository. Jenkins successfully allocated an agent, checked out the target branch, and sequentially executed the defined stages, resulting in a successful build.
```
    Started by user emre
    Obtained Jenkinsfile from git https://github.com/emrearabacioglu/java-maven-app.git
    [Pipeline] Start of Pipeline
    [Pipeline] node
    Running on Jenkins in /var/jenkins_home/workspace/my-pipeline
    [Pipeline] {
    [Pipeline] stage
    [Pipeline] { (Declarative: Checkout SCM)
    [Pipeline] checkout
    The recommended git tool is: git
    using credential github-credentials
    Cloning the remote Git repository
    Cloning repository https://github.com/emrearabacioglu/java-maven-app.git
     > git init /var/jenkins_home/workspace/my-pipeline # timeout=10
    Fetching upstream changes from https://github.com/emrearabacioglu/java-maven-app.git
     > git --version # timeout=10
     > git --version # 'git version 2.47.3'
    using GIT_ASKPASS to set credentials github-credentials
     > git fetch --tags --force --progress -- https://github.com/emrearabacioglu/java-maven-app.git +refs/heads/*:refs/remotes/origin/* # timeout=10
     > git config remote.origin.url https://github.com/emrearabacioglu/java-maven-app.git # timeout=10
     > git config --add remote.origin.fetch +refs/heads/*:refs/remotes/origin/* # timeout=10
    Avoid second fetch
     > git rev-parse refs/remotes/origin/jenkins-jobs^{commit} # timeout=10
    Checking out Revision 80b3d98f6d6378f14c67581b5f84384185b43576 (refs/remotes/origin/jenkins-jobs)
     > git config core.sparsecheckout # timeout=10
     > git checkout -f 80b3d98f6d6378f14c67581b5f84384185b43576 # timeout=10
    Commit message: "Update Jenkinsfile"
    First time build. Skipping changelog.
    [Pipeline] }
    [Pipeline] // stage
    [Pipeline] withEnv
    [Pipeline] {
    [Pipeline] stage
    [Pipeline] { (build)
    [Pipeline] echo
    building the application...
    [Pipeline] }
    [Pipeline] // stage
    [Pipeline] stage
    [Pipeline] { (test)
    [Pipeline] echo
    Testing the application...
    [Pipeline] }
    [Pipeline] // stage
    [Pipeline] stage
    [Pipeline] { (Deploy)
    [Pipeline] echo
    Deploying the application...
    [Pipeline] }
    [Pipeline] // stage
    [Pipeline] }
    [Pipeline] // withEnv
    [Pipeline] }
    [Pipeline] // node
    [Pipeline] End of Pipeline
    Finished: SUCCESS
```
#### Command Summary
* `pipeline {}`: The mandatory root block that defines a Declarative Pipeline structure.
* `agent any`: Instructs Jenkins to allocate any available executor/node to run the entire pipeline or a specific stage.
* `stage('...') {}`: Defines a distinct, logical phase of the delivery process (e.g., Build, Test, Deploy).
* `steps {}`: Contains the executable tasks and commands that actually perform the work within a stage.
* `echo '...'`: Prints a string message to the Jenkins console output, primarily used for logging and debugging stage progress.
 
</details>

******

<details>
<summary>Jenkinsfile Syntax</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Create full Pipeline</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Introduction to Multibranch Job</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Wrap Up Jenkins Job</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Credentials in Jenkins</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Jenkins Shared Library</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Trigger Jenkins Job - Webhook</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Versioning your application - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Versioning your application - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>
