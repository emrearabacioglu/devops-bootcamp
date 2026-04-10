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
<summary>Create full Pipeline</summary>
 <br />
 
### End-to-End CI Pipeline Implementation with Externalized Groovy Scripting

#### Pipeline Configuration Source Codes
Orchestrated a declarative Jenkins pipeline utilizing Maven as the build tool. To ensure a scalable and maintainable CI/CD architecture, the core execution logic was decoupled from the main Jenkinsfile and abstracted into an external script.groovy module. 

**Jenkinsfile:**
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
**script.groovy:**
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
#### Application Compilation and Packaging
Executed the externalized buildJar function to trigger the Maven build lifecycle. The pipeline successfully compiled the Java source code, validated the build via automated unit tests, and generated a distributable JAR artifact within the pipeline workspace.
```text
    [Pipeline] { (build jar)
    [Pipeline] tool
    [Pipeline] envVarsForTool
    [Pipeline] withEnv
    [Pipeline] {
    [Pipeline] script
    [Pipeline] {
    [Pipeline] echo
    building the application..
    [Pipeline] sh
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
#### Secure Containerization and DockerHub Publishing
Engineered the buildImage stage to autonomously construct a Docker image encapsulating the newly compiled JAR. Leveraged Jenkins withCredentials to securely inject DockerHub credentials, ensuring sensitive data (passwords/tokens) remained completely masked in the console outputs. The tagged artifact (jma-2.0) was successfully pushed to the private DockerHub repository.
```text
    [Pipeline] { (build image)
    ...
    [Pipeline] echo
    building the docker image...
    [Pipeline] withCredentials
    Masking supported pattern matches of $PASS
    [Pipeline] {
    [Pipeline] sh
    + docker build -t emrearabacioglu/demo-app:jma-2.0 .
    ...
    #9 writing image sha256:8f23d27432b0b31924fb939992d46b840db46de0ef4858009c6bb0993716cb37 done
    #9 naming to docker.io/emrearabacioglu/demo-app:jma-2.0 done
    ...
    [Pipeline] sh
    + echo ****
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    [Pipeline] sh
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
<summary>Jenkins Shared Library</summary>
 <br />
 
### Extending CI/CD Pipelines with Jenkins Shared Libraries

#### Configuration & Script Ecosystem
Abstracted pipeline execution logic into globally accessible Groovy classes and scripts by implementing a Jenkins Shared Library. This modular approach enabled logic reuse, parameterization, and direct library resolution within the pipeline scope.

Jenkinsfile:

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

script.groovy:

    def deployApp() {
        echo 'deploying the application...'
    }
    return this

docker.groovy (Class implementation):

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

buildImage.groovy:

    #!/user/bin/env groovy
    import com.example.Docker

    def call(String imageName) {
        return new Docker(this).buildDockerImage(imageName)
    }

buildJar.groovy:

    #!/user/bin/env groovy
    def call() {
        echo "building the application.. for branch $GIT_BRANCH"
        sh 'mvn package'
    }

dockerLogin.groovy:

    #!/user/bin/env groovy
    import com.example.Docker

    def call() {
        return new Docker(this).dockerLogin()
    }

dockerPush.groovy:

    #!/user/bin/env groovy
    import com.example.Docker

    def call(String imageName) {
        return new Docker(this).dockerPush(imageName)
    }

#### Shared Library Integration & Initialization
Demonstrated dynamic project-scoped loading of the Shared Library from a remote Git repository directly inside the `Jenkinsfile` using the `library` identifier block.

    [Pipeline] Start of Pipeline
    [Pipeline] library
    Loading library jenkins-shared-library@master
    Attempting to resolve master from remote references...
     > git fetch --no-tags --force --progress -- https://github.com/emrearabacioglu/jenkins-shared-library.git +refs/heads/*:refs/remotes/origin/* # timeout=10
    Checking out Revision 5d73a3e1ca7d6e3a1f0246abb0c83e847e08ac1d (master)
    Commit message: "Update Docker.groovy"

#### Application Compilation via Shared Library
Successfully utilized the custom `buildJar()` step injected by the Shared Library. The pipeline dynamically captured the Git branch environment variable and executed the Maven build phase.

    [Pipeline] echo
    building the application.. for branch jenkins-shared-lib
    [Pipeline] sh
    + mvn package
    [INFO] Scanning for projects...
    [INFO] Building java-maven-app 1.1.0-SNAPSHOT
    ...
    [INFO] Replacing main artifact /var/jenkins_home/workspace/ice-user-auth_jenkins-shared-lib/target/java-maven-app-1.1.0-SNAPSHOT.jar
    [INFO] BUILD SUCCESS
    [INFO] Total time:  2.719 s
    [INFO] Finished at: 2026-04-07T09:33:54Z

#### Containerization & DockerHub Publishing via Groovy Classes
Executed complex logic through the instantiated `com.example.Docker` Groovy class. Passed parameters from the `Jenkinsfile` directly to the class methods (`buildDockerImage`, `dockerLogin`, `dockerPush`) to build and securely publish the tagged artifact (`jma-3.0`).

    [Pipeline] echo
    building the docker image...
    [Pipeline] sh
    + docker build -t emrearabacioglu/demo-app:jma-3.0 .
    ...
    #9 writing image sha256:1ea4dc8739a586e103b99d529dd9447cc7ec6436428777b3ecbc104dce5fe57e done
    #9 naming to docker.io/emrearabacioglu/demo-app:jma-3.0 done
    ...
    [Pipeline] echo
    Logging into Docker Repository...
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    ...
    [Pipeline] echo
    pushing the docker image...
    [Pipeline] sh
    + docker push emrearabacioglu/demo-app:jma-3.0
    The push refers to repository [docker.io/emrearabacioglu/demo-app]
    jma-3.0: digest: sha256:3c815248c19e549f5f3a04844d7bb86614a8de79d2965be158e84003c6aa6c17 size: 1159
    Finished: SUCCESS

 
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
