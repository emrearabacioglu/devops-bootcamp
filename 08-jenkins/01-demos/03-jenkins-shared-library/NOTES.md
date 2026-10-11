# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create a Jenkins Shared Library

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
