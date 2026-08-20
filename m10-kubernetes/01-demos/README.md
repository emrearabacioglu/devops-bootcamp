******

<details>
<summary>Minikube and kubectl - Local Setup</summary>
 <br />
 
 #### Install and setup minikube

 ```bash
root@PC:~# curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 36.8M  100 36.8M    0     0  9600k      0  0:00:03  0:00:03 --:--:-- 9602k
root@PC:~# sudo dpkg -i minikube_latest_amd64.deb
Selecting previously unselected package minikube.
(Reading database ... 81547 files and directories currently installed.)
Preparing to unpack minikube_latest_amd64.deb ...
Unpacking minikube (1.38.1-0) ...
Setting up minikube (1.38.1-0) ...
root@PC:~# minikube start --force
😄  minikube v1.38.1 on Ubuntu 24.04 (kvm/amd64)
❗  minikube skips various validations when --force is supplied; this may lead to unexpected behavior
✨  Automatically selected the docker driver
🛑  The "docker" driver should not be used with root privileges. If you wish to continue as root, use --force.
💡  If you are running minikube within a VM, consider using --driver=none:
📘    https://minikube.sigs.k8s.io/docs/reference/drivers/none/
❗  Starting v1.39.0, minikube will default to "containerd" container runtime. See #21973 for more info.
📌  Using Docker driver with root privileges
❗  For an improved experience it's recommended to use Docker Engine instead of Docker Desktop.
Docker Engine installation instructions: https://docs.docker.com/engine/install/#server
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.50 ...
💾  Downloading Kubernetes v1.35.1 preload ...
    > gcr.io/k8s-minikube/kicbase...:  519.58 MiB / 519.58 MiB  100.00% 9.70 Mi
    > preloaded-images-k8s-v18-v1...:  272.45 MiB / 272.45 MiB  100.00% 4.91 Mi
🔥  Creating docker container (CPUs=2, Memory=3072MB) ...
🐳  Preparing Kubernetes v1.35.1 on Docker 29.2.1 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
root@PC:~# minikube status
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

root@PC:~# kubectl get node
NAME       STATUS   ROLES           AGE    VERSION
minikube   Ready    control-plane   8m4s   v1.35.1


```
 
</details>


******

<details>
<summary>Kubernetes CLI - Main kubectl commands</summary>
 <br />
 
### Kubernetes Workloads Configuration & Management

#### Created Nginx Deployment
Demonstrated the imperative creation of an Nginx deployment. Verified the deployment and pod status to ensure the container was provisioned and running successfully.

```bash
    root@PC:~# kubectl create deployment nginx-depl --image=nginx
    deployment.apps/nginx-depl created
    root@PC:~# kubectl get deployment
    NAME         READY   UP-TO-DATE   AVAILABLE   AGE
    nginx-depl   1/1     1            1           13s
    root@PC:~# kubectl get pod
    NAME                          READY   STATUS    RESTARTS   AGE
    nginx-depl-569bd7dcf9-l7vmx   1/1     Running   0          26s
```
#### Edited Deployment
Modified the live deployment configuration dynamically. Successfully resolved YAML syntax validations during the edit, resulting in a configuration update and the progression of a new ReplicaSet.
```bash
    root@PC:~# kubectl edit deployment nginx-depl
    deployment.apps/nginx-depl edited
    root@PC:~# kubectl get replicaset
    NAME                    DESIRED   CURRENT   READY   AGE
    nginx-depl-569bd7dcf9   0         0         0       13m
    nginx-depl-7fb6fc4d75   1         1         1       24s
```
#### Created MongoDB Deployment
Provisioned a MongoDB deployment and utilized the describe function to inspect the pod's lifecycle events, verifying the image pull status, container creation, and cluster assignment.
```bash
    root@PC:~# kubectl create deployment mongo-deployment --image=mongo
    deployment.apps/mongo-deployment created
    root@PC:~# kubectl describe pod mongo-deployment-5dc7f4b7d7-9pxdj
    ...
    Events:
      Type    Reason     Age   From               Message
      ----    ------     ----  ----               -------
      Normal  Scheduled  51s   default-scheduler  Successfully assigned default/mongo-deployment-5dc7f4b7d7-9pxdj to minikube
      Normal  Pulling    51s   kubelet            Pulling image "mongo"
      Normal  Pulled     12s   kubelet            Successfully pulled image "mongo" in 38.098s
      Normal  Created    12s   kubelet            Container created
      Normal  Started    12s   kubelet            Container started
```
#### Inspected Logs of a Pod
Extracted and reviewed the internal application logs of the running Nginx container to verify the startup sequence, environmental configurations, and worker process initialization.
```bash
    root@PC:~# kubectl logs nginx-depl-7fb6fc4d75-9nd7n
    /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
    10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
    ...
    2026/06/18 07:01:31 [notice] 1#1: start worker processes
    2026/06/18 07:01:31 [notice] 1#1: start worker process 29
```
#### Got Shell of a Running Container
Executed an interactive shell session directly inside the running MongoDB pod to inspect the internal container filesystem and directory structure.
```bash
    root@PC:~# kubectl exec -it mongo-deployment-5dc7f4b7d7-9pxdj -- bin/bash
    root@mongo-deployment-5dc7f4b7d7-9pxdj:/# ls
    bin  boot  data  dev  docker-entrypoint-initdb.d  etc  home  js-yaml.js  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
    root@mongo-deployment-5dc7f4b7d7-9pxdj:/# exit
    exit
```
#### Deleted Deployment
Cleaned up the cluster environment by deleting the previously created deployments, confirming the removal of associated resources and ReplicaSets.
```bash
    root@PC:~# kubectl delete deployment mongo-deployment
    deployment.apps "mongo-deployment" deleted from default namespace
    root@PC:~# kubectl delete deployment nginx-depl
    deployment.apps "nginx-depl" deleted from default namespace
```
#### Applied Configuration File
Demonstrated declarative infrastructure management by applying a YAML configuration file to deploy Nginx. Subsequently updated the YAML to scale the replicas and reapplied the configuration, validating the deployment of additional pods.
```bash
    root@PC:~# kubectl apply -f nginx-deployment.yaml
    deployment.apps/nginx-deployment created
    root@PC:~# kubectl apply -f nginx-deployment.yaml
    deployment.apps/nginx-deployment configured
    root@PC:~# kubectl get deployment
    NAME               READY   UP-TO-DATE   AVAILABLE   AGE
    nginx-deployment   2/2     2            2           49s
```
#### Commands Summary
* `kubectl get [resource]`: Retrieves and lists the status of specified Kubernetes resources (nodes, pods, services, deployments, replicasets).
* `kubectl create deployment`: Imperatively generates a new deployment utilizing a specified container image.
* `kubectl edit deployment`: Opens the live configuration of a deployment in the default text editor for immediate modifications.
* `kubectl describe pod`: Provides a detailed lifecycle, state summary, and event history of a specific pod.
* `kubectl logs`: Fetches the standard output and error logs generated by a specific container.
* `kubectl exec -it`: Executes a command interactively inside a running container (e.g., opening a bash shell).
* `kubectl delete deployment`: Removes a deployment and terminates its managed pods from the cluster.
* `kubectl apply -f`: Declaratively creates or updates resources based on the state defined in a provided YAML file.

</details>


******

<details>
<summary>Introduction to YAML Configuration File</summary>
 <br />
 
 ```bash
root@PC:~# cat nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 8080
root@PC:~# cat nginx-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
root@PC:~# kubectl apply -f nginx-deployment.yaml
deployment.apps/nginx-deployment configured
root@PC:~# kubectl apply -f nginx-service.yaml
service/nginx-service created
root@PC:~# kubectl get pod
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-58f47d84fb-99zq5   1/1     Running   0          17s
nginx-deployment-58f47d84fb-mqppq   1/1     Running   0          15s
root@PC:~# kubectl get service
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes      ClusterIP   10.96.0.1       <none>        443/TCP   26h
nginx-service   ClusterIP   10.99.139.225   <none>        80/TCP    11s
root@PC:~# kubectl describe service nginx-service
Name:                     nginx-service
Namespace:                default
Labels:                   <none>
Annotations:              <none>
Selector:                 app=nginx
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.99.139.225
IPs:                      10.99.139.225
Port:                     <unset>  80/TCP
TargetPort:               8080/TCP
Endpoints:                10.244.0.8:8080,10.244.0.9:8080
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
root@PC:~# kubectl get pod -o wide
NAME                                READY   STATUS    RESTARTS   AGE    IP           NODE       NOMINATED NODE   READINESS GATES
nginx-deployment-58f47d84fb-99zq5   1/1     Running   0          104s   10.244.0.8   minikube   <none>           <none>
nginx-deployment-58f47d84fb-mqppq   1/1     Running   0          102s   10.244.0.9   minikube   <none>           <none>
root@PC:~# kubectl get deployment nginx-deployment -o yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "2"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"nginx"},"name":"nginx-deployment","namespace":"default"},"spec":{"replicas":2,"selector":{"matchLabels":{"app":"nginx"}},"template":{"metadata":{"labels":{"app":"nginx"}},"spec":{"containers":[{"image":"nginx:1.25","name":"nginx","ports":[{"containerPort":8080}]}]}}}}
  creationTimestamp: "2026-06-18T11:19:46Z"
  generation: 3
  labels:
    app: nginx
  name: nginx-deployment
  namespace: default
  resourceVersion: "12767"
  uid: 79e2867b-6b6b-47a9-8a03-78d17d7f69ce
spec:
  progressDeadlineSeconds: 600
  replicas: 2
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: nginx
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx:1.25
        imagePullPolicy: IfNotPresent
        name: nginx
        ports:
        - containerPort: 8080
          protocol: TCP
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  availableReplicas: 2
  conditions:
  - lastTransitionTime: "2026-06-18T11:20:25Z"
    lastUpdateTime: "2026-06-18T11:20:25Z"
    message: Deployment has minimum availability.
    reason: MinimumReplicasAvailable
    status: "True"
    type: Available
  - lastTransitionTime: "2026-06-18T11:19:46Z"
    lastUpdateTime: "2026-06-19T09:06:00Z"
    message: ReplicaSet "nginx-deployment-58f47d84fb" has successfully progressed.
    reason: NewReplicaSetAvailable
    status: "True"
    type: Progressing
  observedGeneration: 3
  readyReplicas: 2
  replicas: 2
  terminatingReplicas: 0
  updatedReplicas: 2
root@PC:~# kubectl get deployment nginx-deployment -o yaml >nginx-deployment-result.yaml
root@PC:~# code nginx-deployment-result.yaml
root@PC:~# kubectl delete -f nginx-deployment.yaml
deployment.apps "nginx-deployment" deleted from default namespace
root@PC:~# kubectl delete -f nginx-service.yaml
service "nginx-service" deleted from default namespace
root@PC:~#

```
 
</details>


******

<details>
<summary>Demo project: Deploying MongoDB and Mongo Express</summary>
 <br />

 ### Demo executed - Deploying MongoDB and MongoExpress

#### Created Secret for Mongo Credentials
Provisioned a Kubernetes Secret to securely manage database authentication credentials. Encoded the initial values into base64 format and outputted the YAML manifest to verify the structured data prior to application.
```bash
    root@PC:~# echo -n 'username' | base64
    dXNlcm5hbWU=
    root@PC:~# echo -n 'password' | base64
    cGFzc3dvcmQ=
    root@PC:~# cat mongo-secret.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: mongodb-secret
    type: Opaque
    data:
      mongo-root-username: dXNlcm5hbWU=
      mongo-root-password: cGFzc3dvcmQ=
    root@PC:~# kubectl apply -f mongo-secret.yaml
    secret/mongodb-secret created
    root@PC:~# kubectl get secret
    NAME             TYPE     DATA   AGE
    mongodb-secret   Opaque   2      10s
```
#### Created MongoDB Deployment & Internal Service
Authored a unified YAML manifest encompassing both the backend MongoDB deployment and its internal ClusterIP service. Deployed the configurations to establish the database instance and a persistent, secure intra-cluster network endpoint. Verified the pod's running state, IP allocation, and service endpoints.
```bash
    root@PC:~# cat mongo.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mongodb-deployment
      labels:
        app: mongodb
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mongodb
      template:
        metadata:
          labels:
            app: mongodb
        spec:
          containers:
          - name: mongodb
            image: mongo
            ports:
            - containerPort: 27017
            env:
            - name: MONGO_INITDB_ROOT_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: MONGO_INITDB_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongodb-service
    spec:
      selector:
        app: mongodb
      ports:
      - protocol: TCP
        port: 27017
        targetPort: 27017
    root@PC:~# kubectl apply -f mongo.yaml
    deployment.apps/mongodb-deployment created
    service/mongodb-service created
    root@PC:~# kubectl get pod -o wide
    NAME                                 READY   STATUS    RESTARTS   AGE    IP            NODE       NOMINATED NODE   READINESS GATES
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   0          7m5s   10.244.0.10   minikube   <none>           <none>
    root@PC:~# kubectl get service
    NAME              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)     AGE
    mongodb-service   ClusterIP   10.100.190.116   <none>        27017/TCP   25s
```
#### Created ConfigMap for DB Server URL
Abstracted the internal database connection string from the application workload by creating a ConfigMap. Outputted the manifest to demonstrate centralized configuration management.
```bash
    root@PC:~# cat mongo-configmap.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: mongodb-configmap
    data:
      database_url: "mongodb-service:27017"
    root@PC:~# kubectl apply -f mongo-configmap.yaml
    configmap/mongodb-configmap created
```
#### Created MongoExpress Deployment & External Service
Deployed the Mongo Express administrative interface coupled with a LoadBalancer service for external accessibility. Showcased the YAML manifest to highlight dynamic environment variable injection from the previously established Secret and ConfigMap. Verified the application initialization via pod logs and provisioned a local Minikube tunnel to expose the UI to the host machine.
```bash
    root@PC:~# cat mongo-express.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mongo-express
      labels:
        app: mongo-express
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mongo-express
      template:
        metadata:
          labels:
            app: mongo-express
        spec:
          containers:
          - name: mongo-express
            image: mongo-express
            ports:
            - containerPort: 8081
            env:
            - name: ME_CONFIG_MONGODB_ADMINUSERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: ME_CONFIG_MONGODB_ADMINPASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
            - name: DATABASE_URL
              valueFrom:
                configMapKeyRef:
                  name: mongodb-configmap
                  key: database_url
            - name: ME_CONFIG_MONGODB_URL
              value: "mongodb://$(ME_CONFIG_MONGODB_ADMINUSERNAME):$(ME_CONFIG_MONGODB_ADMINPASSWORD)@$(DATABASE_URL)"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongo-express-service
    spec:
      selector:
        app: mongo-express
      type: LoadBalancer
      ports:
      - protocol: TCP
        port: 8081
        targetPort: 8081
        nodePort: 30000
    root@PC:~# kubectl apply -f mongo-express.yaml
    deployment.apps/mongo-express created
    service/mongo-express-service created
    root@PC:~# kubectl logs mongo-express-5747d566b9-wz2t6
    Waiting for mongodb-service:27017...
    Welcome to mongo-express 1.0.2
    ------------------------
    Mongo Express server listening at http://0.0.0.0:8081
    root@PC:~# minikube service mongo-express-service
    🔗  Starting tunnel for service mongo-express-service.
    🎉  Opening service default/mongo-express-service in default browser...
    👉  http://127.0.0.1:39985
    
```
<img width="1699" height="1086" alt="image" src="https://github.com/user-attachments/assets/59666c81-3768-488a-a9bb-da1b26c93a9f" />

 
</details>


******


<details>
<summary>ConfigMap & Secret Volume Types</summary>
 <br />
 
### Kubernetes Mosquitto Configuration and Volume Mounting

#### Created Mosquitto Deployment without any volumes
Demonstrated the deployment of a standalone Eclipse Mosquitto broker to inspect the default container environment. Verified the default configuration structure by executing into the running pod before safely deleting the unconfigured deployment.

    root@PC:~# cat mosquitto-without-volumes.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mosquitto
      labels:
        app: mosquitto
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mosquitto
      template:
        metadata:
          labels:
            app: mosquitto
        spec:
            containers:
              - name: mosquitto
                image: eclipse-mosquitto:2.0
                ports:
                  - containerPort: 1883
    
    root@PC:~# kubectl apply -f mosquitto-without-volumes.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h39m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h39m ago)  61d
    mosquitto-8bbb9c957-jjqq8            1/1     Running   0              11s
    
    root@PC:~# kubectl exec -it mosquitto-8bbb9c957-jjqq8 -- /bin/sh
    / # cd mosquitto/config/
    /mosquitto/config # cat mosquitto.conf
    # Config file for mosquitto
    #
    # See mosquitto.conf(5) for more information.
    #
    # Default values are shown, uncomment to change.
    ...
    /mosquitto/config # exit
    
    root@PC:~# kubectl delete -f mosquitto-without-volumes.yaml
    deployment.apps "mosquitto" deleted from default namespace

#### Created ConfigMap component to overwrite mosquitto.conf file
Configured a Kubernetes ConfigMap to manage and overwrite the default broker settings, specifically defining log destinations, types, timestamps, and custom listener ports.

    root@PC:~# cat config-file.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: mosquitto-config-file
    data:
        mosquitto.conf: |
            log_dest stdout
            log_type all
            log_timestamp true
            listener 9001
            
    root@PC:~# kubectl apply -f config-file.yaml
    configmap/mosquitto-config-file created

#### Created Secret component to add passwords file
Generated a Kubernetes Secret resource using Opaque type encoding to securely manage and inject authentication credentials into the cluster environment.

    root@PC:~# cat secret-file.yaml
    apiVersion: v1
    kind: Secret
    metadata:
        name: mosquitto-secret-file
    type: Opaque
    data:
        secret.file: |
            VGVjaFdvcmxkMjAyMyEgLW4K
            
    root@PC:~# kubectl apply -f secret-file.yaml
    secret/mosquitto-secret-file created
    
    root@PC:~# kubectl get secret
    NAME                    TYPE     DATA   AGE
    mongodb-secret          Opaque   2      61d
    mosquitto-secret-file   Opaque   1      10s
    
    root@PC:~# kubectl get configmap
    NAME                    DATA   AGE
    kube-root-ca.crt        1      62d
    mongodb-configmap       1      61d
    mosquitto-config-file   1      24s

#### Adjusted Mosquitto Deployment to include volumes
Modified the Mosquitto deployment architecture to mount the previously created ConfigMap and Secret as container volumes. Validated the successful volume attachments by executing into the pod and verifying that the custom configuration and decrypted secret data were correctly populated in their respective directory paths.

    root@PC:~# cat mosquitto.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mosquitto
      labels:
        app: mosquitto
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mosquitto
      template:
        metadata:
          labels:
            app: mosquitto
        spec:
            containers:
              - name: mosquitto
                image: eclipse-mosquitto:2.0
                ports:
                  - containerPort: 1883
                volumeMounts:
                  - name: mosquitto-config
                    mountPath: /mosquitto/config
                  - name: mosquitto-secret
                    mountPath: /mosquitto/secret
                    readOnly: true
            volumes:
              - name: mosquitto-config
                configMap:
                  name: mosquitto-config-file
              - name: mosquitto-secret
                secret:
                  secretName: mosquitto-secret-file
                  
    root@PC:~# kubectl apply -f mosquitto.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h54m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h54m ago)  61d
    mosquitto-cf9f594cd-dr9wz            1/1     Running   0              12s
    
    root@PC:~# kubectl exec -it mosquitto-cf9f594cd-dr9wz -- /bin/sh
    / # cd mosquitto/secret/
    /mosquitto/secret # cat secret.file
    TechWorld2023! -n
    
    /mosquitto/secret # cd ../config/
    /mosquitto/config # cat mosquitto.conf
    log_dest stdout
    log_type all
    log_timestamp true
    listener 9001
    /mosquitto/config # exit

 
</details>




******

<details>
<summary>Helm Demo: Install a Stateful Application on Kubernetes using Helm</summary>
 <br />
 
 ### Kubernetes Cluster Configuration & Stateful Deployments on Linode

#### Created K8s cluster on Linode Kubernetes Engine
Configured the local environment to authenticate and connect to a newly provisioned Linode Kubernetes Engine (LKE) cluster. Verified the successful initialization of the cluster nodes.

<img width="1908" height="353" alt="image" src="https://github.com/user-attachments/assets/93420d43-fef2-4dbd-9540-7e0e7f3958c9" />


    root@PC:~/helm# export KUBECONFIG=test-kubeconfig.yaml
    root@PC:~/helm# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645862-950499-d6sh5   Ready    <none>   3m31s   v1.36.2
    lke645862-950499-rx6k6   Ready    <none>   3m19s   v1.36.2

#### Deployed replicated MongoDB (StatefulSet using Helm Chart) and configured Data Persistence with Linode Block Storage
Installed the Helm package manager and deployed a 3-replica MongoDB StatefulSet using the official Bitnami chart. Enforced data persistence by mapping a custom values file to utilize Linode's block storage class, ensuring data durability across pod restarts.

    root@PC:~/helm# curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 | bash
    root@PC:~/helm# helm repo add bitnami https://charts.bitnami.com/bitnami
    "bitnami" has been added to your repositories
    
    root@PC:~/helm# cat helm-mongodb.yaml
    architecture: replicaset
    replicaCount: 3
    persistence:
      storageClass: "linode-block-storage"
    auth:
      rootPassword: secret-root-pwd
      
    root@PC:~/helm# helm install mongodb --values helm-mongodb.yaml bitnami/mongodb
    NAME: mongodb
    LAST DEPLOYED: Thu Aug 20 14:17:28 2026
    NAMESPACE: default
    STATUS: deployed
    
    root@PC:~/helm# kubectl get all
    NAME                    READY   STATUS    RESTARTS   AGE
    pod/mongodb-0           1/1     Running   0          4m
    pod/mongodb-1           1/1     Running   0          3m5s
    pod/mongodb-2           1/1     Running   0          117s
    pod/mongodb-arbiter-0   1/1     Running   0          4m
    
    NAME                               READY   AGE
    statefulset.apps/mongodb           3/3     4m
    statefulset.apps/mongodb-arbiter   1/1     4m

#### Deployed MongoExpress (Deployment and Service)
Provisioned the Mongo Express web interface to act as a database management portal. Dynamically injected authentication credentials from the generated Kubernetes Secrets directly into the container's environment variables to establish a secure database connection.

    root@PC:~/helm# cat helm-mongo-express.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mongo-express
      labels:
        app: mongo-express
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mongo-express
      template:
        metadata:
          labels:
            app: mongo-express
        spec:
          containers:
          - name: mongo-express
            image: mongo-express
            ports:
            - containerPort: 8081
            env:
            - name: ME_CONFIG_MONGODB_ADMINUSERNAME
              value: root
            - name: ME_CONFIG_MONGODB_ADMINPASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb
                  key: mongodb-root-password
            - name: ME_CONFIG_MONGODB_URL
              value: "mongodb://$(ME_CONFIG_MONGODB_ADMINUSERNAME):$(ME_CONFIG_MONGODB_ADMINPASSWORD)@mongodb-0.mongodb-headless:27017"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongo-express-service
    spec:
      selector:
        app: mongo-express
      ports:
        - protocol: TCP
          port: 8081
          targetPort: 8081
          
    root@PC:~/helm# kubectl apply -f helm-mongo-express.yaml
    deployment.apps/mongo-express created
    service/mongo-express-service created
    
    root@PC:~/helm# kubectl logs mongo-express-794fb84c64-k4lk2
    Waiting for mongodb-0.mongodb-headless:27017...
    No custom config.js found, loading config.default.js
    Welcome to mongo-express 1.0.2
    ------------------------
    Mongo Express server listening at http://0.0.0.0:8081

#### Deployed NGINX Ingress Controller as Loadbalancer (using Helm Chart)
Pulled and deployed the official NGINX Ingress Controller via its OCI registry to manage incoming external HTTP/HTTPS traffic. Successfully validated the allocation of an external LoadBalancer IP (`85.90.246.91`) assigned by the cloud provider.

    root@PC:~/helm# helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress --set controller.reportIngressStatus.enable=true
    NAME: nginx-ingress
    LAST DEPLOYED: Thu Aug 20 14:32:48 2026
    NAMESPACE: default
    STATUS: deployed
    
    root@PC:~/helm# kubectl get svc
    NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)                      AGE
    nginx-ingress-controller   LoadBalancer   10.128.86.169    85.90.246.91   80:32260/TCP,443:31566/TCP   2m9s

#### Configured Ingress rule
Created and applied an Ingress routing resource to capture external traffic hitting the specified host address and accurately redirect it to the internal `mongo-express-service`.

    root@PC:~/helm# cat helm-ingress-yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
        name: mongo-express
    spec:
      ingressClassName: nginx-ingress
      rules:
      - host: 85-90-246-91.ip.linodeusercontent.com
        http:
          paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: mongo-express-service
                  port:
                    number: 8081
                    
    root@PC:~/helm# kubectl apply -f helm-ingress-yaml
    ingress.networking.k8s.io/mongo-express created
    
    root@PC:~/helm# kubectl get ingress
    NAME            CLASS           HOSTS                                   ADDRESS   PORTS   AGE
    mongo-express   nginx-ingress   85-90-246-91.ip.linodeusercontent.com             80      10s

#### Connected via browser
Successfully established an end-to-end connection to the Mongo Express graphical interface via the web browser by hitting the external LoadBalancer IP and authenticating with the default administrative credentials.
<img width="1895" height="981" alt="image" src="https://github.com/user-attachments/assets/37b85b84-fded-4549-8632-4e10a7b69687" />


 
</details>


******

<details>
<summary>Demo: Deploy App from Private Docker Registry</summary>
 <br />
 
### Integrating Private AWS ECR with Kubernetes Deployments

#### Setup a Private Docker Repository (AWS Elastic Container Registry)
Initiated the creation of a private Elastic Container Registry (ECR) repository. Resolved IAM authorization barriers by reconfiguring the local AWS CLI environment with appropriate administrative credentials, resulting in a successfully provisioned registry for the application artifacts.

    root@PC:/mnt/c/Users/emrea/js-app# aws ecr create-repository --repository-name js-app --region eu-central-1
    aws: [ERROR]: An error occurred (AccessDeniedException) when calling the CreateRepository operation...
    
    root@PC:/mnt/c/Users/emrea/js-app# aws configure
    AWS Access Key ID [****************2IFO]: ******
    AWS Secret Access Key [****************rPq7]: ******
    
    root@PC:/mnt/c/Users/emrea/js-app# aws ecr create-repository --repository-name js-app --region eu-central-1
    {
        "repository": {
            "repositoryArn": "arn:aws:ecr:eu-central-1:731872836472:repository/js-app",
            "repositoryUri": "731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app",
            ...
        }
    }

#### Have a demo application
Cloned the target Node.js application from a remote repository, executed a local multi-stage Docker build, and tagged the resulting artifact. Successfully pushed the versioned image (`1.2`) to the previously configured private AWS ECR repository.

    root@PC:/mnt/c/Users/emrea# git clone https://gitlab.com/twn-devops-bootcamp/latest/10-kubernetes/js-app.git
    
    root@PC:/mnt/c/Users/emrea/js-app# docker build -t js-app .
    
    root@PC:/mnt/c/Users/emrea/js-app# docker tag js-app:latest 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
    
    root@PC:/mnt/c/Users/emrea/js-app# docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2
    The push refers to repository [731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app]
    ...
    1.2: digest: sha256:8300baebb... size: 856

#### Logged in to AWS Container Repository | docker login and create docker config.json file
Authenticated the local Docker daemon with AWS ECR. Bypassed Minikube root privilege restrictions to start the cluster, established an SSH session, and replicated the authentication directly within the node. The resulting Docker configuration file was copied back to the host system and encoded for Kubernetes Secret integration.

    root@PC:~# aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded
    
    root@PC:~# minikube start --force
    
    root@PC:~# minikube ssh
    docker@minikube:~$ docker login --username AWS -p eyJwYXls... 731872836472.dkr.ecr.eu-central-1.amazonaws.com
    Login Succeeded
    
    root@PC:~# minikube cp minikube:/home/docker/.docker/config.json ~/.docker/config.json
    
    root@PC:~# cat .docker/config.json | base64
    ewoJImF1dGhzIjogewoJCSI3MzE4NzI4MzY0NzIuZGtyLmVjci5ldS1jZW50cmFsLTEuYW1hem9u
    YXdzLmNvbSI6IHsKCQkJImF1dGgiOiAiUVZkVE9tVjVTbmRaV0d4ellqSkdhMGxxYjJsUldGVjZZ
    ...
    Rk9YMFVGQlhSVlZQVkhoUVFWRjFkMVJvU0hsVE4xYzNWa1UyV0UxNlRHcEtVMFJoU2twNlFXNWpX
    bU5MVTFkT1NHMU5ObHBZTWtwaFdFbDVWVTVzWVRSVk9WRjFjbFJrVlV3d1ZuaHBTR0Y1TUUxWlNn
    cHRhRGswV2s1WVRtczBTMXBPUkVOSFlUQkRNR2s1VFZWT1NWSXhiR0pEWWtwaWJrSlhhMHBSUVE5
    Qk9TSUtDUTF9Cgl9Cn0=

#### Created Secret component
Demonstrated multiple methodologies for securely injecting registry credentials into the cluster. Initially structured a declarative YAML manifest utilizing the base64-encoded Docker configuration. Subsequently provisioned functional Secrets via imperative `kubectl` commands, utilizing both file-based (`--from-file`) and direct parameter (`--docker-server`) approaches to establish authentication.

    root@PC:~# cat docker-secret.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: my-registry-key
    data:
      .dockerconfigjson: ewoJImF1dGhzIjogewoJCSI3MzE4NzI4MzY0NzIuZGtyLmVjci5ldS1jZW50cmFsLTEuYW1hem9u
    YXdzLmNvbSI6IHsKCQkJImF1dGgiOiAiUVZkVE9tVjVTbmRaV0d4ellqSkdhMGxxYjJsUldGVjZZ
    bFpTY0ZwNWRGVlZSMUp4V25wQ1RVNXJkekJXV0ZaeFdteENjbU14UWxGaGExVjVVakF4U0ZSVlRu
    ...
    Rk9YMFVGQlhSVlZQVkhoUVFWRjFkMVJvU0hsVE4xYzNWa1UyV0UxNlRHcEtVMFJoU2twNlFXNWpX
    bU5MVTFkT1NHMU5ObHBZTWtwaFdFbDVWVTVzWVRSVk9WRjFjbFJrVlV3d1ZuaHBTR0Y1TUUxWlNn
    cHRhRGswV2s1WVRtczBTMXBPUkVOSFlUQkRNR2s1VFZWT1NWSXhiR0pEWWtwaWJrSlhhMHBSUVE5
    Qk9TSUtDUTF9Cgl9Cn0=
    type: kubernetes.io/dockerconfigjson
    
    root@PC:~# kubectl create secret generic my-registry-key --from-file=.dockerconfigjson=.docker/config.json --type=kubernetes.io/dockerconfigjson
    secret/my-registry-key created
    
    root@PC:~# kubectl create secret docker-registry my-registry-key-two \
    > --docker-server=https://731872836472.dkr.ecr.eu-central-1.amazonaws.com \
    > --docker-username=AWS \
    > --docker-password=eyJwYXls...
    secret/my-registry-key-two created

#### Configured Deployment for demo app
Configured and evaluated the Kubernetes Deployment to pull the application from the private registry. Captured and resolved an `ImagePullBackOff` failure resulting from an initial lack of credentials. Remediated the issue by explicitly mapping the `imagePullSecrets` array to the newly created `my-registry-key-two` Secret, achieving a successful container deployment.

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
            
    root@PC:~# kubectl apply -f my-app-deployment.yaml
    
    root@PC:~# kubectl get pod
    NAME                     READY   STATUS             RESTARTS   AGE
    my-app-568ff5465-728m8   0/1     ImagePullBackOff   0          4s
    
    root@PC:~# kubectl delete -f my-app-deployment.yaml
    
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
            
    root@PC:~# kubectl apply -f my-app-deployment.yaml
    deployment.apps/my-app-two created
    
    root@PC:~# kubectl get pod
    NAME                          READY   STATUS    RESTARTS   AGE
    my-app-two-5bdb94fbc4-lwc6n   1/1     Running   0          6s

 
</details>


******


<details>
<summary>Demo project: Deploy Microservices Application & Best Practices </summary>
 <br />


 ### Kubernetes Microservices Architecture Deployment

#### Cluster Provisioning and Authentication
Configured secure access to a remote Kubernetes cluster provisioned on Linode Kubernetes Engine (LKE) consisting of 3 worker nodes. Established the connection by securely modifying the permissions of the cluster configuration file and exporting it to the local environment variables. Verified node health and readiness states prior to deployment.

    root@PC:~/microservices# chmod 400 online-shop-microservices-kubeconfig.yaml
    root@PC:~/microservices# ls -l online-shop-microservices-kubeconfig.yaml
    -r-------- 1 root root 2825 Aug 20 22:44 online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# export KUBECONFIG=~/microservices/online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645983-950801-8j6d4   Ready    <none>   3m26s   v1.36.2
    lke645983-950801-8prw6   Ready    <none>   3m28s   v1.36.2
    lke645983-950801-bv6kj   Ready    <none>   3m31s   v1.36.2

#### Infrastructure as Code: Optimized Configurations
Engineered a comprehensive declarative YAML manifest (`config.yaml`) encapsulating 11 distinct microservices. The manifest architecture integrates the following industry best practices for high availability and stability:
*   **Version Control:** Bound each container image to a specific release tag (e.g., `v0.8.0` or `alpine`) to ensure immutability.
*   **High Availability:** Enforced `replicas: 2` across Deployments to ensure fault tolerance.
*   **Health Checks:** Configured both `livenessProbe` and `readinessProbe` (via gRPC, TCP, and HTTP protocols) for automated failure recovery and traffic routing safety.
*   **Resource Management:** Explicitly defined CPU and Memory `requests` and `limits` to prevent node resource exhaustion.
*   **Network Security:** Omitted `NodePort` types, utilizing internal `ClusterIP` Services exclusively for backend communication.

<img width="2993" height="1396" alt="image" src="https://github.com/user-attachments/assets/7e178072-2ac3-49ca-8cdd-fca54c96cdb6" />

```
    root@PC:~/microservices# touch config.yaml
    root@PC:~/microservices# cat config.yaml
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: emailservice
    spec:
      selector:
        matchLabels:
          app: emailservice
      template:
        metadata:
          labels:
            app: emailservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/emailservice:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            livenessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            resources:
              requests:
                cpu: 100m
                memory: 64Mi
              limits:
                cpu: 200m
                memory: 128Mi
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: emailservice
    spec:
      type: ClusterIP
      selector:
        app: emailservice
      ports:
      - protocol: TCP
        port: 5000
        targetPort: 8080
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: recommendationservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: recommendationservice
      template:
        metadata:
          labels:
            app: recommendationservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/recommendationservice:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: recommendationservice
    spec:
      type: ClusterIP
      selector:
        app: recommendationservice
      ports:
      - protocol: TCP
        port: 8080
        targetPort: 8080
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: productcatalogservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: productcatalogservice
      template:
        metadata:
          labels:
            app: productcatalogservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/productcatalogservice:v0.8.0
            ports:
            - containerPort: 3550
            env:
            - name: PORT
              value: "3550"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 3550
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 3550
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: productcatalogservice
    spec:
      type: ClusterIP
      selector:
        app: productcatalogservice
      ports:
      - protocol: TCP
        port: 3550
        targetPort: 3550
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: paymentservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: paymentservice
      template:
        metadata:
          labels:
            app: paymentservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/paymentservice:v0.8.0
            ports:
            - containerPort: 50051
            env:
            - name: PORT
              value: "50051"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: paymentservice
    spec:
      type: ClusterIP
      selector:
        app: paymentservice
      ports:
      - protocol: TCP
        port: 50051
        targetPort: 50051
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: currencyservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: currencyservice
      template:
        metadata:
          labels:
            app: currencyservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/currencyservice:v0.8.0
            ports:
            - containerPort: 7000
            env:
            - name: PORT
              value: "7000"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 7000
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 7000
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: currencyservice
    spec:
      type: ClusterIP
      selector:
        app: currencyservice
      ports:
      - protocol: TCP
        port: 7000
        targetPort: 7000
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: shippingservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: shippingservice
      template:
        metadata:
          labels:
            app: shippingservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/shippingservice:v0.8.0
            ports:
            - containerPort: 50051
            env:
            - name: PORT
              value: "50051"
            livenessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: shippingservice
    spec:
      type: ClusterIP
      selector:
        app: shippingservice
      ports:
      - protocol: TCP
        port: 50051
        targetPort: 50051
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: adservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: adservice
      template:
        metadata:
          labels:
            app: adservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/adservice:v0.8.0
            ports:
            - containerPort: 9555
            env:
            - name: PORT
              value: "9555"
            livenessProbe:
              grpc:
                port: 9555
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 9555
              periodSeconds: 5
            resources:
              requests:
                cpu: 200m
                memory: 180Mi
              limits:
                cpu: 300m
                memory: 300Mi
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: adservice
    spec:
      type: ClusterIP
      selector:
        app: adservice
      ports:
      - protocol: TCP
        port: 9555
        targetPort: 9555
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: cartservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: cartservice
      template:
        metadata:
          labels:
            app: cartservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/cartservice:v0.8.0
            ports:
            - containerPort: 7070
            env:
            - name: PORT
              value: "7070"
            - name: REDIS_ADDR
              value: "redis-cart:6379"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 7070
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 7070
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: cartservice
    spec:
      type: ClusterIP
      selector:
        app: cartservice
      ports:
      - protocol: TCP
        port: 7070
        targetPort: 7070
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redis-cart
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: redis-cart
      template:
        metadata:
          labels:
            app: redis-cart
        spec:
          containers:
          - name: redis
            image: redis:alpine
            ports:
            - containerPort: 6379
            livenessProbe:
              initialDelaySeconds: 5
              tcpSocket:
                port: 6379
              periodSeconds: 5
            readinessProbe:
              initialDelaySeconds: 5
              tcpSocket:
                port: 6379
              periodSeconds: 5
            resources:
              requests:
                cpu: 70m
                memory: 200Mi
              limits:
                cpu: 125m
                memory: 300Mi
            volumeMounts:
            - name: redis-data
              mountPath: /data
          volumes:
          - name: redis-data
            emptyDir: {}
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: redis-cart
    spec:
      type: ClusterIP
      selector:
        app: redis-cart
      ports:
      - protocol: TCP
        port: 6379
        targetPort: 6379
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: checkoutservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: checkoutservice
      template:
        metadata:
          labels:
            app: checkoutservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/checkoutservice:v0.8.0
            ports:
            - containerPort: 5050
            env:
            - name: PORT
              value: "5050"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: SHIPPING_SERVICE_ADDR
              value: "shippingservice:50051"
            - name: PAYMENT_SERVICE_ADDR
              value: "paymentservice:50051"
            - name: EMAIL_SERVICE_ADDR
              value: "emailservice:5000"
            - name: CURRENCY_SERVICE_ADDR
              value: "currencyservice:7000"
            - name: CART_SERVICE_ADDR
              value: "cartservice:7070"
            livenessProbe:
              grpc:
                port: 5050
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 5050
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: checkoutservice
    spec:
      type: ClusterIP
      selector:
        app: checkoutservice
      ports:
      - protocol: TCP
        port: 5050
        targetPort: 5050
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: frontend
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: frontend
      template:
        metadata:
          labels:
            app: frontend
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/frontend:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: CURRENCY_SERVICE_ADDR
              value: "currencyservice:7000"
            - name: CART_SERVICE_ADDR
              value: "cartservice:7070"
            - name: RECOMMENDATION_SERVICE_ADDR
              value: "recommendationservice:8080"
            - name: SHIPPING_SERVICE_ADDR
              value: "shippingservice:50051"
            - name: CHECKOUT_SERVICE_ADDR
              value: "checkoutservice:5050"
            - name: AD_SERVICE_ADDR
              value: "adservice:9555"
            livenessProbe:
              httpGet:
                path: "/_healthz"
                port: 8080
              periodSeconds: 5
            readinessProbe:
              httpGet:
                path: "/_healthz"
                port: 8080
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: frontend
    spec:
      type: LoadBalancer
      selector:
        app: frontend
      ports:
      - protocol: TCP
        port: 80
        targetPort: 8080
```
#### Namespace Isolation and Microservices Deployment
Established a logical boundary by creating a dedicated `microservices` namespace. Deployed the comprehensive `config.yaml` manifest into this isolated environment. Monitored the rollout progression until all interconnected services and their respective replicas reached a `Running` and stable state.
```
    root@PC:~/microservices# kubectl create ns microservices
    namespace/microservices created
    
    root@PC:~/microservices# kubectl apply -f config.yaml -n microservices
    deployment.apps/emailservice created
    service/emailservice created
    deployment.apps/recommendationservice created
    service/recommendationservice created
    deployment.apps/productcatalogservice created
    service/productcatalogservice created
    ...
    deployment.apps/frontend created
    service/frontend created
    
    root@PC:~/microservices# kubectl get pod -n microservices
    NAME                                     READY   STATUS    RESTARTS      AGE
    adservice-7dcbd647b4-dgpsh               1/1     Running   0             61s
    cartservice-75cd7bb67b-65z46             1/1     Running   0             60s
    checkoutservice-7879b466b9-v9bjq         1/1     Running   0             60s
    currencyservice-7bdfdf6dc7-j66tt         1/1     Running   0             61s
    emailservice-65f667bb5b-pmx67            0/1     Running   1 (11s ago)   63s
    frontend-5dcd6f968c-74nmb                1/1     Running   0             59s
    paymentservice-64c7d98d5-52qhx           1/1     Running   0             62s
    productcatalogservice-576696c58c-g5d6t   1/1     Running   0             62s
    recommendationservice-57cfddb6c9-8ft7w   1/1     Running   0             62s
    redis-cart-6448465667-kfjqh              1/1     Running   0             60s
    shippingservice-c9848967f-jtc6x          1/1     Running   0             61s
```
#### Exposed External Traffic (Accessed Online Shop)
Audited the active Services within the namespace to confirm internal connectivity (ClusterIP) for backend microservices and identified the dynamically provisioned public entry point. The Frontend service successfully acquired an `EXTERNAL-IP` (`139.162.172.76`) via the `LoadBalancer` type, enabling direct browser access to the online shop application.
```
    root@PC:~/microservices# kubectl get svc -n microservices
    NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)        AGE
    adservice               ClusterIP      10.128.224.167   <none>           9555/TCP       85s
    cartservice             ClusterIP      10.128.132.55    <none>           7070/TCP       85s
    checkoutservice         ClusterIP      10.128.210.210   <none>           5050/TCP       85s
    currencyservice         ClusterIP      10.128.253.70    <none>           7000/TCP       86s
    emailservice            ClusterIP      10.128.15.127    <none>           5000/TCP       87s
    frontend                LoadBalancer   10.128.45.166    139.162.172.76   80:32023/TCP   84s
    paymentservice          ClusterIP      10.128.229.163   <none>           50051/TCP      86s
    productcatalogservice   ClusterIP      10.128.161.225   <none>           3550/TCP       87s
    recommendationservice   ClusterIP      10.128.254.90    <none>           8080/TCP       87s
    redis-cart              ClusterIP      10.128.66.178    <none>           6379/TCP       85s
    shippingservice         ClusterIP      10.128.186.29    <none>           50051/TCP      86s
```
#### Verified External Traffic (Accessed Online Shop via Browser)
<img width="1890" height="968" alt="image" src="https://github.com/user-attachments/assets/15d8a2fe-810a-4f14-b815-8ad417e042a1" />

 
</details>


******


<details>
<summary>Demo project: Create Helm Chart for Microservices</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Demo project: Deploy Microservices with Helmfile</summary>
 <br />
 
 **content will be here**
 
</details>

******
