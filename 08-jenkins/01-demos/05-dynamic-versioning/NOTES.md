# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Dynamically Increment Application version in Jenkins Pipeline

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
