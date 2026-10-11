# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Complete CI/CD Pipeline with EKS and private DockerHub registry

### Demo Executed: Build, push to DockerHub and deploy to EKS

#### envsubst in the Jenkins Container
The Kubernetes manifests use variables like `$APP_NAME`, so Jenkins needs `envsubst` to fill them in. Installed `gettext-base` (which has `envsubst`) in the Jenkins container:

    root@PC:~/k8s-on-aws# ssh root@164.90.179.224
    ...
    root@jenkins:~# docker exec -u 0  -it 4b8376846d81 bash
    root@4b8376846d81:/# apt-get install gettext-base
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    The following NEW packages will be installed:
      gettext-base
    ...
    Unpacking gettext-base (0.23.1-2) ...
    Setting up gettext-base (0.23.1-2) ...
    root@4b8376846d81:/# envsubst
    ^C
    root@4b8376846d81:/# exit

#### Registry Secret
Created a `docker-registry` secret (`my-registry-key`) with my DockerHub login, so the nodes can pull the private `demo-app` image. Also deleted the nginx deployment from the previous demo:

    root@PC:~/k8s-on-aws# kubectl get node
    NAME                                             STATUS   ROLES    AGE     VERSION
    ip-192-168-26-26.eu-central-1.compute.internal   Ready    <none>   7h34m   v1.36.3-eks-cb19647
    ip-192-168-68-99.eu-central-1.compute.internal   Ready    <none>   7h35m   v1.36.3-eks-cb19647
    
    root@PC:~/k8s-on-aws# kubectl create secret docker-registry my-registry-key \
    > --docker-server=docker.io \
    > --docker-username=emrearabacioglu \
    > --docker-password=***
    secret/my-registry-key created
    
    root@PC:~/k8s-on-aws# kubectl get secret
    NAME              TYPE                              DATA   AGE
    my-registry-key   kubernetes.io/dockerconfigjson    1      8s
    
    root@PC:~/k8s-on-aws# kubectl delete deployment nginx-deployment
    deployment.apps "nginx-deployment" deleted from default namespace

#### Deployment and Service Manifests
`deployment.yaml` uses `imagePullSecrets` with the registry key. App name and image tag are variables (`$APP_NAME`, `$IMAGE_NAME`). `service.yaml` is a ClusterIP service:

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
            - name: my-registry-key
          containers:
            - name: $APP_NAME
              image: emrearabacioglu/demo-app:$IMAGE_NAME
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

#### Jenkinsfile
The pipeline bumps the version with Maven, builds the jar and the image, and pushes it to DockerHub. The deploy stage pipes the manifests through `envsubst` into `kubectl apply`. The last stage commits the version bump to the `jenkins-jobs` branch:

    Jenkinsfile:
    #!/usr/bin/env groovy
    pipeline {
        agent any
        tools {
            maven 'maven-3.9'
        }
        environment {
            DOCKER_REPO = 'emrearabacioglu/demo-app'
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
            // ... [build app & build image stages omitted for brevity] ...
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

#### Pipeline Run and Checks
Pipeline output: deploy applied the manifests and the version bump was pushed:

    Started by user emre
    ...
    + envsubst
    + kubectl apply -f -
    deployment.apps/java-maven-app configured
    + envsubst
    + kubectl apply -f -
    service/java-maven-app unchanged
    ...
    + git commit -m ci: version bump
    [detached HEAD 6329e06] ci: version bump
    ...
    + git push origin HEAD:jenkins-jobs
    To https://github.com/emrearabacioglu/java-maven-app.git
       321573d..6329e06  HEAD -> jenkins-jobs
    ...
    Finished: SUCCESS

At first a pod was `Pending`. `kubectl describe` showed `Too many pods`: the t2.micro nodes hit their pod limit (ENI limit):

    root@PC:~/k8s-on-aws# kubectl describe pod java-maven-app-6d9b6c84cf-8m6bd
    ...
    Events:
      Type     Reason            Age    From               Message
      ----     ------            ----   ----               -------
      Warning  FailedScheduling  6m6s   default-scheduler  0/2 nodes are available: 2 Too many pods. no new claims to deallocate...

Once there was room for them, both replicas were `Running`. Deployment and service:

    root@PC:~/k8s-on-aws# kubectl get pod
    NAME                              READY   STATUS    RESTARTS   AGE
    java-maven-app-646744859d-8wgxv   1/1     Running   0          9m58s
    java-maven-app-646744859d-czzr6   1/1     Running   0          3m2s
    
    root@PC:~/k8s-on-aws# kubectl get deployment
    NAME             READY   UP-TO-DATE   AVAILABLE   AGE
    java-maven-app   2/2     2            2           13m
    
    root@PC:~/k8s-on-aws# kubectl get service
    NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
    java-maven-app   ClusterIP   10.100.41.247   <none>        80/TCP    13m

<img width="1909" height="733" alt="image" src="https://github.com/user-attachments/assets/97fa43d3-621e-40a5-9b98-2706ad5ec804" />

<img width="1895" height="813" alt="image" src="https://github.com/user-attachments/assets/19f9cd07-f26b-4f52-9107-67ff873bd7c2" />
