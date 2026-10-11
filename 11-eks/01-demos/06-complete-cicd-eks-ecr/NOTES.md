# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Complete CI/CD Pipeline with EKS and AWS ECR

### Demo Executed: Same pipeline with ECR instead of DockerHub

#### ECR Repository and Jenkins Credentials
Created an ECR repository for the app image in the AWS console, and added ECR credentials in Jenkins so the pipeline can push to it:

<img width="1702" height="365" alt="image" src="https://github.com/user-attachments/assets/6ec9e46f-6b29-4fa4-afb8-77df594ecee6" />

<img width="1704" height="747" alt="image" src="https://github.com/user-attachments/assets/32b62a9d-78e6-4282-867c-4a8cb42adb72" />

#### Registry Secret for ECR
Created a second `docker-registry` secret (`aws-registry-key`) for ECR. Username is `AWS`, password is the ECR authorization token:

    root@PC:~/k8s-on-aws# kubectl get secret
    NAME              TYPE                              DATA   AGE
    my-registry-key   kubernetes.io/dockerconfigjson    1      72m
    
    root@PC:~/k8s-on-aws# kubectl create secret docker-registry aws-registry-key \
    --docker-server=731872836472.dkr.ecr.eu-central-1.amazonaws.com \
    --docker-username=AWS \
    --docker-password=***
    secret/aws-registry-key created

#### Manifests
`deployment.yaml` now uses `aws-registry-key` and the ECR image URL. `service.yaml` is unchanged:

    deployment.yaml:
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: $APP_NAME
      labels:
        app: $APP_NAME
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: $APP_NAME
      template:
        metadata:
          labels:
            app: $APP_NAME
        spec:
          imagePullSecrets:
            - name: aws-registry-key
          containers:
            - name: $APP_NAME
              image: 731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-maven-app:$IMAGE_NAME
              imagePullPolicy: Always
              ports:
                - containerPort: 8080
    
    service.yaml:
    apiVersion: v1
    kind: Service
    metadata:
      name: $APP_NAME
    spec:
      selector:
        app: $APP_NAME
      ports:
        - protocol: TCP
          port: 80
          targetPort: 8080

#### Jenkinsfile and Pipeline Run
Changed the `Jenkinsfile` to push to ECR: added `DOCKER_REPO_SERVER`, and the build image stage logs in with the `ecr-credentials`. The rest (version bump, deploy with `envsubst`, commit) is the same. Below the Jenkinsfile is the console output of the run: ECR login and push, deploy, version bump commit:

    Jenkinsfile:
    #!/usr/bin/env groovy
    pipeline {
        agent any
        tools {
            maven 'maven-3.9'
        }
        environment {
            DOCKER_REPO_SERVER = '731872836472.dkr.ecr.eu-central-1.amazonaws.com'
            DOCKER_REPO = "${DOCKER_REPO_SERVER}/java-maven-app"
        }
        stages {
            stage('increment version') {
                steps {
                    script {
                        echo 'incrementing app version...'
                        sh 'mvn build-helper:parse-version versions:set \
                            -DnewVersion=\\${parsedVersion.majorVersion}.\\${parsedVersion.minorVersion}.\\${parsedVersion.nextIncrementalVersion} \
                            versions:commit'
                        def matcher = readFile('pom.xml') =~ '<version>(.+)</version>'
                        def version = matcher[0][1]
                        env.IMAGE_NAME = "$version-$BUILD_NUMBER"
                    }
                }
            }
            stage('build app') {
                steps {
                    script {
                        echo 'building the application...'
                        sh 'mvn clean package'
                    }
                }
            }
            stage('build image') {
                steps {
                    script {
                        echo "building the docker image..."
                        withCredentials([usernamePassword(credentialsId: 'ecr-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]){
                            sh "docker build -t ${DOCKER_REPO}:${IMAGE_NAME} ."
                            sh "echo $PASS | docker login -u $USER --password-stdin ${DOCKER_REPO_SERVER}"
                            sh "docker push ${DOCKER_REPO}:${IMAGE_NAME}"
                        }
                    }
                }
            }
            stage('deploy') {
                environment {
                    AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                    AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_access_secret_key')
                    APP_NAME = 'java-maven-app'
                }
                steps {
                    script {
                       echo 'deploying docker image...'
                       sh 'envsubst < kubernetes/deployment.yaml | kubectl apply -f -'
                       sh 'envsubst < kubernetes/service.yaml | kubectl apply -f -'
                    }
                }
            }
            stage('commit version update'){
                steps {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]){
                            sh "git remote set-url origin https://${USER}:${PASS}@github.com/emrearabacioglu/java-maven-app.git"
                            sh 'git add .'
                            sh 'git commit -m "ci: version bump"'
                            sh 'git push origin HEAD:jenkins-jobs'
                        }
                    }
                }
            }
        }
    }

    Jenkins Build console output:
    Started by user emre
    ...
    + docker login -u AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded
    + docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-maven-app:1.1.14-6
    The push refers to repository [731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-maven-app]
    ...
    4fe17990842d: Pushed
    1.1.14-6: digest: sha256:fd04029134d36686a798ba497135e16ed898d58cc3da2a94c123e94854b903b6 size: 1159
    ...
    + envsubst
    + kubectl apply -f -
    deployment.apps/java-maven-app created
    + envsubst
    + kubectl apply -f -
    service/java-maven-app unchanged
    ...
    + git commit -m ci: version bump
    [detached HEAD c1b158f] ci: version bump
     4 files changed, 7 insertions(+), 7 deletions(-)
    + git push origin HEAD:jenkins-jobs
    To https://github.com/emrearabacioglu/java-maven-app.git
       ef42f60..c1b158f  HEAD -> jenkins-jobs
    ...
    Finished: SUCCESS

#### Result on the Cluster
Both pods running with the new ECR image:

    root@PC:~/k8s-on-aws# kubectl get pod
    NAME                              READY   STATUS    RESTARTS   AGE
    java-maven-app-f5bb74f54-2kxj5    1/1     Running   0          3m9s
    java-maven-app-f5bb74f54-k4s7r    1/1     Running   0          3m9s

<img width="1558" height="479" alt="image" src="https://github.com/user-attachments/assets/ebe48e45-1f1f-44ae-bf1e-5de92027e33d" />
<img width="1700" height="609" alt="image" src="https://github.com/user-attachments/assets/36fcb2e5-dc0a-43bb-8d66-e5861fe1d806" />
