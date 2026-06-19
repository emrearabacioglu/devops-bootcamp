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
 
 **content will be here**
 
</details>


******

<details>
<summary>Organizing components with Namespaces</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Kubernetes Services</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Kubernetes Ingress</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Persisting Data with Volumes</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>ConfigMap & Secret Volume Types</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Deploying stateful Apps with StatefulSet</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Introduction to Managed Kubernetes Services</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Helm - Package Manager of Kubernetes</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Helm Demo: Install a Stateful Application on Kubernetes using Helm</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Demo: Deploy App from Private Docker Registry</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Extending the K8s API with Operators</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Secure your cluster - Authorization with RBAC</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Microservices in Kubernetes</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Demo project: Deploy Microservices Application</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Production & Security Best Practices</summary>
 <br />
 
 **content will be here**
 
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
