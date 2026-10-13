# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## CD - Deploy to EKS cluster from Jenkins Pipeline

### Demo Executed: Jenkins deploys nginx to the eksctl cluster

#### kubectl and aws-iam-authenticator in the Jenkins Container
Connected to the Jenkins droplet on DigitalOcean, opened a root shell in the Jenkins container and installed `kubectl` and `aws-iam-authenticator` into `/usr/local/bin`:

```bash
    root@PC:/mnt/c/Users/emrea# ssh root@164.90.179.224
    ...
    root@jenkins:~# docker ps
    CONTAINER ID   IMAGE                 COMMAND                  CREATED        STATUS         PORTS                                                                                      NAMES
    4b8376846d81   jenkins/jenkins:lts   "/usr/bin/tini -- /u…"   5 months ago   Up 4 minutes   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:50000->50000/tcp, [::]:50000->50000/tcp   wizardly_johnson
    
    root@jenkins:~# docker exec -u 0 -it 4b8376846d81 bash
    root@4b8376846d81:/# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl; chmod +x ./kubectl; mv ./kubectl /usr/local/bin/kubectl
    ...
    root@4b8376846d81:/# kubectl version
    Client Version: v1.31.0
    ...
    root@4b8376846d81:/# curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.11/aws-iam-authenticator_0.6.11_linux_amd64
    ...
    root@4b8376846d81:/# chmod +x ./aws-iam-authenticator
    root@4b8376846d81:/# mv ./aws-iam-authenticator /usr/local/bin/
```

#### kubeconfig for Jenkins
Wrote a kubeconfig on the droplet with the EKS endpoint, the CA data and `aws-iam-authenticator` as the auth command. Then created `.kube` in the Jenkins home (`/var/jenkins_home`) as the jenkins user and copied the file into it:
```bash
    root@jenkins:~# cat config
    apiVersion: v1
    kind: Config
    clusters:
    - cluster:
        certificate-authority-data: ***
        server: https://5463C9E961ED09599F5BA27042808CF5.gr7.eu-central-1.eks.amazonaws.com
      name: kubernetes
    contexts:
    - context:
        cluster: kubernetes
        user: aws
      name: aws
    current-context: aws
    users:
    - name: aws
      user:
        exec:
          apiVersion: client.authentication.k8s.io/v1beta1
          command: /usr/local/bin/aws-iam-authenticator
          args:
            - "token"
            - "-i"
            - "demo-cluster"
    
    root@jenkins:~# docker exec -it 4b8376846d81 bash
    jenkins@4b8376846d81:/$ cd ~
    jenkins@4b8376846d81:~$ mkdir .kube
    jenkins@4b8376846d81:~$ exit
    
    root@jenkins:~# docker cp config 4b8376846d81:/var/jenkins_home/.kube/
    Successfully copied 3.58kB to 4b8376846d81:/var/jenkins_home/.kube/
```

#### AWS Credentials and Jenkinsfile
Added the AWS access key ID and secret key as Jenkins credentials:

<img width="1694" height="865" alt="image" src="https://github.com/user-attachments/assets/594b03d6-ad3c-47a5-818b-4a497dc7612b" />

The `Jenkinsfile`. The deploy stage loads the two credentials as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` and creates an nginx deployment with `kubectl`:

```
    #!/usr/bin/env groovy
    
    pipeline {
        agent any
        stages {
            stage('build app') {
                steps {
                   script {
                       echo "building the application..."
                   }
                }
            }
            stage('build image') {
                steps {
                    script {
                        echo "building the docker image..."
                    }
                }
            }
            stage('deploy') {
                environment {
                    AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                    AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_access_secret_key')
                }
                steps {
                    script {
                       echo 'deploying docker image...'
                       sh 'kubectl create deployment nginx-deployment --image=nginx'
                    }
                }
            }
        }
    }
```

#### Pipeline Run

<img width="1024" height="385" alt="image" src="https://github.com/user-attachments/assets/1bfd0e90-a06b-43f5-a646-d96f8e0f89d2" />

Deploy stage output. Jenkins masks the AWS keys and `kubectl` creates the deployment:

```
    Started by user emre
    ...
    Masking supported pattern matches of $AWS_ACCESS_KEY_ID or $AWS_SECRET_ACCESS_KEY
    ...
    deploying docker image...
    + kubectl create deployment nginx-deployment --image=nginx
    deployment.apps/nginx-deployment created
    ...
    Finished: SUCCESS
```

The pod on the cluster, checked from my machine (still `Pending` at that point):

```
    root@PC:/mnt/c/Users/emrea# kubectl get pod
    NAME                                READY   STATUS    RESTARTS   AGE
    nginx-deployment-7d6869886d-bvbm6   0/1     Pending   0          4m52s
```
