# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy our web application in K8s cluster from private Docker registry

### Demo Executed: Pull an image from AWS ECR into Minikube

#### Setup a Private Docker Repository (AWS Elastic Container Registry)
Creating the ECR repository failed at first with an access error:

    root@PC:/mnt/c/Users/emrea/js-app# aws ecr create-repository --repository-name js-app --region eu-central-1
    aws: [ERROR]: An error occurred (AccessDeniedException) when calling the CreateRepository operation...

Ran `aws configure` again with admin credentials:

    root@PC:/mnt/c/Users/emrea/js-app# aws configure
    AWS Access Key ID [****************2IFO]: ******
    AWS Secret Access Key [****************rPq7]: ******

Then the repository was created:

    root@PC:/mnt/c/Users/emrea/js-app# aws ecr create-repository --repository-name js-app --region eu-central-1
    {
        "repository": {
            "repositoryArn": "arn:aws:ecr:eu-central-1:731872836472:repository/js-app",
            "repositoryUri": "731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app",
            ...
        }
    }

#### Have a demo application
Cloned the Node.js demo app, built the image, tagged it with the ECR URL and pushed version `1.2`:

    root@PC:/mnt/c/Users/emrea# git clone https://gitlab.com/twn-devops-bootcamp/latest/10-kubernetes/js-app.git
    
    root@PC:/mnt/c/Users/emrea/js-app# docker build -t js-app .
    
    root@PC:/mnt/c/Users/emrea/js-app# docker tag js-app:latest 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
    
    root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
    The push refers to repository [731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app]
    ...
    1.2: digest: sha256:8300baebb... size: 856

#### Logged in to AWS Container Repository | docker login and create docker config.json file
Logged Docker in to ECR on the host:

    root@PC:~# aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded

Started Minikube (again with `--force` because of root):

    root@PC:~# minikube start --force

Logged in to ECR inside the Minikube node too:

    root@PC:~# minikube ssh
    docker@minikube:~$ docker login --username AWS -p *** 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded

Copied the node's `config.json` to the host and encoded it with base64 for the Secret:

    root@PC:~# minikube cp minikube:/home/docker/.docker/config.json ~/.docker/config.json

    root@PC:~# cat .docker/config.json | base64
    ***

#### Created Secret component
Three ways to create the registry Secret. First a YAML file with the base64 `config.json`:

    root@PC:~# cat docker-secret.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: my-registry-key
    data:
      .dockerconfigjson: ***
    type: kubernetes.io/dockerconfigjson

From the `config.json` file with `kubectl`:

    root@PC:~# kubectl create secret generic my-registry-key --from-file=.dockerconfigjson=.docker/config.json --type=kubernetes.io/dockerconfigjson
    secret/my-registry-key created

With the registry details given directly:

    root@PC:~# kubectl create secret docker-registry my-registry-key-two \
    > --docker-server=https://731872836472.dkr.ecr.eu-central-1.amazonaws.com \
    > --docker-username=AWS \
    > --docker-password=***
    secret/my-registry-key-two created

#### Configured Deployment for demo app
First deployment without any registry credentials:

    root@PC:~# cat my-app-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: my-app
      template:
        metadata:
          labels:
            app: my-app
        spec:
          containers:
          - name: my-app
            image: 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
            imagePullPolicy: Always
            ports:
            - containerPort: 3000

The pod couldn't pull the image:

    root@PC:~# kubectl apply -f my-app-deployment.yaml
    
    root@PC:~# kubectl get pod
    NAME                     READY   STATUS             RESTARTS   AGE
    my-app-568ff5465-728m8   0/1     ImagePullBackOff   0          4s

Deleted it:

    root@PC:~# kubectl delete -f my-app-deployment.yaml

Added `imagePullSecrets` with `my-registry-key-two`:

    root@PC:~# cat my-app-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app-two
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: my-app-two
      template:
        metadata:
          labels:
            app: my-app-two
        spec:
          imagePullSecrets:
          - name: my-registry-key-two
          containers:
          - name: my-app-two
            image: 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
            imagePullPolicy: Always
            ports:
            - containerPort: 3000

This time the image was pulled and the pod is running:

    root@PC:~# kubectl apply -f my-app-deployment.yaml
    deployment.apps/my-app-two created
    
    root@PC:~# kubectl get pod
    NAME                          READY   STATUS    RESTARTS   AGE
    my-app-two-5bdb94fbc4-lwc6n   1/1     Running   0          6s
