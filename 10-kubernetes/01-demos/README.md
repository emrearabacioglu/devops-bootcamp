# Module 10 – Container Orchestration with Kubernetes

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Minikube and kubectl – Local Setup | Install Minikube, start a local cluster, check the node |
| 2 | Main kubectl Commands | Create, edit, inspect, debug and delete Deployments with kubectl |
| 3 | Introduction to YAML Configuration File | Nginx Deployment + Service from YAML, labels/selectors, `-o yaml` status |
| 4 | Deploy MongoDB and Mongo Express into local K8s cluster | Secret, ConfigMap, MongoDB with internal Service, Mongo Express with external Service |
| 5 | Deploy Mosquitto message broker with ConfigMap and Secret Volume Types | Mount a config file and a secret file into the Mosquitto pod |
| 6 | Install a stateful service (MongoDB) on Kubernetes using Helm | Bitnami MongoDB replicaset on LKE, Mongo Express, NGINX Ingress |
| 7 | Deploy our web application in K8s cluster from private Docker registry | Push to ECR, registry Secret, `imagePullSecrets` |
| 8 | Deploy Microservices application in Kubernetes with Production & Security Best Practices | 11 microservices on LKE with probes, resources, fixed tags, own namespace |
| 9 | Create Helm Chart for Microservices | Shared `microservice` chart, values files per service, `redis` chart |
| 10 | Deploy Microservices with Helmfile | `install.sh` with `helm install`, then `helmfile sync/list/destroy` |

## Takeaways

- **Minikube as root:** the docker driver refuses to run as root, so `minikube start --force` was needed (both at setup and before the ECR demo).
- **Imperative vs declarative:** `kubectl create deployment` for quick tests, `kubectl apply -f` for YAML files. Applying the same file again after a change gives `configured`. `kubectl edit deployment` creates a new ReplicaSet and scales the old one to 0.
- **Debugging a pod:** `kubectl describe pod` (Events at the bottom), `kubectl logs <pod>`, `kubectl exec -it <pod> -- bin/bash`.
- **Service to pod connection:** the Service `selector` matches the pod labels and `targetPort` matches the `containerPort`. `kubectl describe service` shows the pod IPs under Endpoints. `kubectl get ... -o yaml` shows the `status` part Kubernetes adds.
- **Secret and ConfigMap as env vars:** Secret values are base64 (`echo -n 'username' | base64`). Pods read them with `secretKeyRef` / `configMapKeyRef`, and env vars can be combined with `$(VAR_NAME)` in another value.
- **Secret and ConfigMap as volumes:** listed under `volumes` (`configMap.name` / `secret.secretName`) and mounted with `volumeMounts`. The files show up in the mount path, the secret already decoded.
- **External access on Minikube:** `minikube service <service-name>` opens a tunnel so the `LoadBalancer` Service can be reached from the host browser.
- **Helm for stateful apps:** `helm repo add` + `helm install --values <file>`. For Bitnami MongoDB: `architecture: replicaset`, `replicaCount: 3`, `persistence.storageClass: "linode-block-storage"`. The root password is in the `mongodb` Secret the chart creates, and the first pod is reachable as `mongodb-0.mongodb-headless:27017`.
- **Ingress:** installed the NGINX Ingress Controller chart from `oci://ghcr.io/nginx/charts/nginx-ingress`. It got a public LoadBalancer IP, and the Ingress rule sends the Linode host name to `mongo-express-service`.
- **Private registry:** without credentials the pod stays in `ImagePullBackOff`. Fixed with a `docker-registry` Secret and `imagePullSecrets` in the pod spec. `aws ecr create-repository` first failed with `AccessDeniedException` until `aws configure` was run with the right user's keys.
- **Microservices config:** fixed image tags, `livenessProbe`/`readinessProbe` (gRPC, TCP, HTTP), resource requests/limits, ClusterIP for backends and a LoadBalancer only for the frontend, all in a separate namespace (`kubectl apply -f config.yaml -n microservices`).
- **Helm chart and Helmfile:** one generic chart with `{{ .Values.x }}` and a `range` loop for env vars, one values file per service. `helm template` and `helm install --dry-run` check the output first. `helmfile sync`, `helmfile list` and `helmfile destroy` replace the `install.sh`/`uninstall.sh` scripts.

******

<details>
<summary>Minikube and kubectl – Local Setup</summary>
 <br />

#### Install and Set Up Minikube
Downloaded and installed the Minikube `.deb` package:

```bash
root@PC:~# curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
...
root@PC:~# sudo dpkg -i minikube_latest_amd64.deb
...
Unpacking minikube (1.38.1-0) ...
Setting up minikube (1.38.1-0) ...
```

Started the cluster. The docker driver doesn't run as root without `--force`:

```bash
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
...
🔥  Creating docker container (CPUs=2, Memory=3072MB) ...
🐳  Preparing Kubernetes v1.35.1 on Docker 29.2.1 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Checked the cluster status and the node:

```bash
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
<summary>Main kubectl Commands</summary>
 <br />

#### Created Nginx Deployment
Created an Nginx deployment from the command line and checked the deployment and pod:

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
Changed the deployment with `kubectl edit`. After a YAML syntax fix in the editor it was saved, and a new ReplicaSet replaced the old one (old one scaled to 0):

```bash
    root@PC:~# kubectl edit deployment nginx-depl
    deployment.apps/nginx-depl edited
    root@PC:~# kubectl get replicaset
    NAME                    DESIRED   CURRENT   READY   AGE
    nginx-depl-569bd7dcf9   0         0         0       13m
    nginx-depl-7fb6fc4d75   1         1         1       24s
```

#### Created MongoDB Deployment
Created a MongoDB deployment and checked the pod events with `describe` (scheduling, image pull, container start):

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
Nginx container logs, from startup to the worker processes:

```bash
    root@PC:~# kubectl logs nginx-depl-7fb6fc4d75-9nd7n
    /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
    10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
    ...
    2026/06/18 07:01:31 [notice] 1#1: start worker processes
    2026/06/18 07:01:31 [notice] 1#1: start worker process 29
```

#### Got Shell of a Running Container
Opened a shell inside the MongoDB pod and listed the filesystem:

```bash
    root@PC:~# kubectl exec -it mongo-deployment-5dc7f4b7d7-9pxdj -- bin/bash
    root@mongo-deployment-5dc7f4b7d7-9pxdj:/# ls
    bin  boot  data  dev  docker-entrypoint-initdb.d  etc  home  js-yaml.js  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
    root@mongo-deployment-5dc7f4b7d7-9pxdj:/# exit
    exit
```

#### Deleted Deployment
Deleted both deployments. Their ReplicaSets and pods go with them:

```bash
    root@PC:~# kubectl delete deployment mongo-deployment
    deployment.apps "mongo-deployment" deleted from default namespace
    root@PC:~# kubectl delete deployment nginx-depl
    deployment.apps "nginx-depl" deleted from default namespace
```

#### Applied Configuration File
Created the Nginx deployment from a YAML file. Then changed the replica count in the file and applied it again:

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
* `kubectl get [resource]`: lists nodes, pods, services, deployments, replicasets.
* `kubectl create deployment`: creates a deployment from an image.
* `kubectl edit deployment`: opens the live deployment config in an editor.
* `kubectl describe pod`: details and events of a pod.
* `kubectl logs`: logs of a container.
* `kubectl exec -it`: runs a command inside a running container, e.g. a bash shell.
* `kubectl delete deployment`: deletes a deployment and its pods.
* `kubectl apply -f`: creates or updates resources from a YAML file.

</details>

******

<details>
<summary>Introduction to YAML Configuration File</summary>
 <br />

#### Deployment and Service Files
The Service selects pods with the label `app: nginx` and forwards port 80 to the container port 8080:

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
```

#### Apply and Check
Applied both files and checked the pods and the service:

```bash
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
```

The service endpoints are the two pod IPs on port 8080:

```bash
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
```

#### Status Generated by Kubernetes
Got the deployment back from the cluster with `-o yaml`. Kubernetes adds default values and a `status` section:

```bash
root@PC:~# kubectl get deployment nginx-deployment -o yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "2"
    kubectl.kubernetes.io/last-applied-configuration: |
...
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
```

Saved this output to a file, then deleted both resources:

```bash
root@PC:~# kubectl get deployment nginx-deployment -o yaml >nginx-deployment-result.yaml
root@PC:~# code nginx-deployment-result.yaml
root@PC:~# kubectl delete -f nginx-deployment.yaml
deployment.apps "nginx-deployment" deleted from default namespace
root@PC:~# kubectl delete -f nginx-service.yaml
service "nginx-service" deleted from default namespace
```

</details>

******

<details>
<summary>Demo Project: Deploy MongoDB and Mongo Express into local K8s cluster</summary>
 <br />

### Demo Executed: MongoDB and Mongo Express on Minikube

#### Created Secret for Mongo Credentials
Encoded the demo username and password with base64 and put them in a Secret:

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
Deployment and internal (ClusterIP) Service for MongoDB in one file, separated by `---`. The root username and password come from the Secret:

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
ConfigMap with the MongoDB service address:

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
Mongo Express gets the credentials from the Secret and the DB address from the ConfigMap. The Service is `LoadBalancer` type with `nodePort: 30000`:

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
```

Applied it and checked the logs. Mongo Express connected to `mongodb-service:27017`:

```bash
    root@PC:~# kubectl apply -f mongo-express.yaml
    deployment.apps/mongo-express created
    service/mongo-express-service created
    root@PC:~# kubectl logs mongo-express-5747d566b9-wz2t6
    Waiting for mongodb-service:27017...
    Welcome to mongo-express 1.0.2
    ------------------------
    Mongo Express server listening at http://0.0.0.0:8081
```

Opened the service from the host with a Minikube tunnel:

```bash
    root@PC:~# minikube service mongo-express-service
    🔗  Starting tunnel for service mongo-express-service.
    🎉  Opening service default/mongo-express-service in default browser...
    👉  http://127.0.0.1:39985
```

<img width="1699" height="1086" alt="image" src="https://github.com/user-attachments/assets/59666c81-3768-488a-a9bb-da1b26c93a9f" />

</details>

******

<details>
<summary>Demo Project: Deploy Mosquitto message broker with ConfigMap and Secret Volume Types</summary>
 <br />

### Demo Executed: Mount a ConfigMap and a Secret into Mosquitto

#### Created Mosquitto Deployment without any volumes
First ran Mosquitto without volumes to see the default config file:

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

Applied it:

    root@PC:~# kubectl apply -f mosquitto-without-volumes.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h39m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h39m ago)  61d
    mosquitto-8bbb9c957-jjqq8            1/1     Running   0              11s

Default `mosquitto.conf` inside the container:

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

Deleted this version:

    root@PC:~# kubectl delete -f mosquitto-without-volumes.yaml
    deployment.apps "mosquitto" deleted from default namespace

#### Created ConfigMap component to overwrite mosquitto.conf file
ConfigMap with a new `mosquitto.conf` (logging settings and listener port 9001):

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
Secret holding a file called `secret.file`:

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

Both the Secret and the ConfigMap are in the cluster:

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
Mounted the ConfigMap to `/mosquitto/config` and the Secret to `/mosquitto/secret` (read-only):

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

Applied it:

    root@PC:~# kubectl apply -f mosquitto.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h54m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h54m ago)  61d
    mosquitto-cf9f594cd-dr9wz            1/1     Running   0              12s

Inside the pod, the secret file is already decoded and `mosquitto.conf` is the one from the ConfigMap:

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
<summary>Demo Project: Install a stateful service (MongoDB) on Kubernetes using Helm</summary>
 <br />

### Demo Executed: MongoDB replicaset with Helm on Linode Kubernetes Engine

#### Created K8s cluster on Linode Kubernetes Engine
Created a 2-node cluster on LKE:

<img width="1908" height="353" alt="image" src="https://github.com/user-attachments/assets/93420d43-fef2-4dbd-9540-7e0e7f3958c9" />

Pointed kubectl to the downloaded kubeconfig file and checked the nodes:

    root@PC:~/helm# export KUBECONFIG=test-kubeconfig.yaml
    root@PC:~/helm# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645862-950499-d6sh5   Ready    <none>   3m31s   v1.36.2
    lke645862-950499-rx6k6   Ready    <none>   3m19s   v1.36.2

#### Deployed replicated MongoDB (StatefulSet using Helm Chart) and configured Data Persistence with Linode Block Storage
Installed Helm and added the Bitnami repo:

    root@PC:~/helm# curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 | bash
    root@PC:~/helm# helm repo add bitnami https://charts.bitnami.com/bitnami
    "bitnami" has been added to your repositories

Values file: 3 replicas, Linode block storage for the volumes, and the root password:

    root@PC:~/helm# cat helm-mongodb.yaml
    architecture: replicaset
    replicaCount: 3
    persistence:
      storageClass: "linode-block-storage"
    auth:
      rootPassword: secret-root-pwd

Installed the chart with this values file:

    root@PC:~/helm# helm install mongodb --values helm-mongodb.yaml bitnami/mongodb
    NAME: mongodb
    LAST DEPLOYED: Thu Aug 20 14:17:28 2026
    NAMESPACE: default
    STATUS: deployed

MongoDB runs as a StatefulSet with 3 pods plus an arbiter:

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
Mongo Express takes the root password from the `mongodb` Secret created by the chart and connects to `mongodb-0.mongodb-headless`:

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

Applied it and checked the logs:

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
Installed the NGINX Ingress Controller chart from its OCI registry. Its service got the external IP `85.90.246.91`:

    root@PC:~/helm# helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress --set controller.reportIngressStatus.enable=true
    NAME: nginx-ingress
    LAST DEPLOYED: Thu Aug 20 14:32:48 2026
    NAMESPACE: default
    STATUS: deployed
    
    root@PC:~/helm# kubectl get svc
    NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)                      AGE
    nginx-ingress-controller   LoadBalancer   10.128.86.169    85.90.246.91   80:32260/TCP,443:31566/TCP   2m9s

#### Configured Ingress rule
Ingress rule that sends requests for the Linode host name to `mongo-express-service`:

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

Applied it:

    root@PC:~/helm# kubectl apply -f helm-ingress-yaml
    ingress.networking.k8s.io/mongo-express created
    
    root@PC:~/helm# kubectl get ingress
    NAME            CLASS           HOSTS                                   ADDRESS   PORTS   AGE
    mongo-express   nginx-ingress   85-90-246-91.ip.linodeusercontent.com             80      10s

#### Connected via browser
Opened Mongo Express in the browser through the Ingress and logged in with the default credentials:

<img width="1895" height="981" alt="image" src="https://github.com/user-attachments/assets/37b85b84-fded-4549-8632-4e10a7b69687" />

</details>

******

<details>
<summary>Demo Project: Deploy our web application in K8s cluster from private Docker registry</summary>
 <br />

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

</details>

******

<details>
<summary>Demo Project: Deploy Microservices application in Kubernetes with Production & Security Best Practices</summary>
 <br />

### Demo Executed: Online shop microservices on LKE

#### Cluster Provisioning and Authentication
Created a 3-node cluster on LKE. Made the kubeconfig file read-only for my user, exported it and checked the nodes:

    root@PC:~/microservices# chmod 400 online-shop-microservices-kubeconfig.yaml
    root@PC:~/microservices# ls -l online-shop-microservices-kubeconfig.yaml
    -r-------- 1 root root 2825 Aug 20 22:44 online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# export KUBECONFIG=~/microservices/online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645983-950801-8j6d4   Ready    <none>   3m26s   v1.36.2
    lke645983-950801-8prw6   Ready    <none>   3m28s   v1.36.2
    lke645983-950801-bv6kj   Ready    <none>   3m31s   v1.36.2

#### Config File with Best Practices
One `config.yaml` with a Deployment and a Service for each of the 11 microservices. What's in it:
*   **Fixed image versions:** every image has a tag (`v0.8.0`, `redis:alpine`), no `latest`.
*   **Replicas:** most Deployments have `replicas: 2`.
*   **Health checks:** `livenessProbe` and `readinessProbe` with gRPC, TCP or HTTP.
*   **Resources:** CPU and memory `requests` and `limits`.
*   **No NodePort:** backend services are `ClusterIP`, only the frontend is a `LoadBalancer`.

<img width="2993" height="1396" alt="image" src="https://github.com/user-attachments/assets/7e178072-2ac3-49ca-8cdd-fca54c96cdb6" />

`config.yaml`:

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
Created a `microservices` namespace and applied the file there. All pods came up:

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
Only the frontend has an external IP (`139.162.172.76`), the other services are ClusterIP:

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
The online shop opened in the browser on the frontend's external IP:

<img width="1890" height="968" alt="image" src="https://github.com/user-attachments/assets/15d8a2fe-810a-4f14-b815-8ad417e042a1" />

</details>

******

<details>
<summary>Demo Project: Create Helm Chart for Microservices</summary>
 <br />

### Demo Executed: One shared chart for the microservices and one for Redis

#### Created “microservices” Helm Chart
Created a chart called `microservice` that can be used for all the stateless services:

    root@PC:~/k8s/microservices# helm create microservice

`deployment.yaml` template. Name, replicas, image, port and env vars come from the values file:

    root@PC:~/k8s/microservices/helmchart/microservice/templates# cat deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {{ .Values.appName }}
    spec:
      replicas: {{ .Values.appReplicas }}
      selector:
        matchLabels:
          app: {{ .Values.appName }}
      template:
        metadata:
          labels:
            app: {{ .Values.appName }}
        spec:
          containers:
          - name: {{ .Values.appName }}
            image: "{{ .Values.appImage }}:{{ .Values.appVersion }}"
            ports:
            - containerPort: {{ .Values.containerPort }}
            env:
            {{- range .Values.containerEnvVars }}
            - name: {{ .name }}
              value: {{ .value | quote }}
            {{- end }}

`service.yaml` template:

    root@PC:~/k8s/microservices/helmchart/microservice/templates# cat service.yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: {{ .Values.appName }}
    spec:
      type: {{ .Values.serviceType }}
      selector:
        app: {{ .Values.appName }}
      ports:
      - protocol: TCP
        port: {{ .Values.servicePort }}
        targetPort: {{ .Values.containerPort }}

#### Created values.yaml files for each microservice
Each service has its own values file, e.g. `email-service-values.yaml`:

    root@PC:~/k8s/microservices# cat email-service-values.yaml
    appName: emailservice
    appImage: gcr.io/google-samples/microservices-demo/emailservice
    appVersion: v0.8.0
    appReplicas: 2
    containerPort: 8080
    containerEnvVars:
    - name: PORT
      value: "8080"
    
    servicePort: 5000

Installed emailservice and recommendationservice on Minikube with the same chart and their own values files:

    root@PC:~/k8s/microservices# helm install -f email-service-values.yaml emailservice microservice
    NAME: emailservice
    LAST DEPLOYED: Fri Aug 21 15:13:00 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    
    root@PC:~/k8s/microservices# helm install -f values/recommendation-service-values.yaml recommendationservice microservice
    NAME: recommendationservice
    LAST DEPLOYED: Fri Aug 21 15:32:00 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1

Pods of both releases:

    root@PC:~/k8s/microservices# kubectl get pod
    NAME                                     READY   STATUS              RESTARTS      AGE
    emailservice-778b6cfbdd-27j5g            1/1     Running             0             19m
    emailservice-778b6cfbdd-9s5xg            1/1     Running             0             19m
    recommendationservice-5f556544d5-5zqbj   1/1     Running             0             11s
    recommendationservice-5f556544d5-wf7f4   0/1     ContainerCreating   0             12s

#### Created “redis” Helm Chart and values file for it
Redis got its own chart, with TCP probes, resource limits and an `emptyDir` volume:

    root@PC:~/k8s/microservices/charts# helm create redis

Rendered the templates with `helm template` to check the output:

    root@PC:~/k8s/microservices# helm template -f values/redis-values.yaml charts/redis
    ---
    # Source: redis/templates/deployment.yaml
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
          - name: redis-cart
            image: "redis:alpine"
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

Ran a dry run before the real install:

    root@PC:~/k8s/microservices# helm install --dry-run -f values/redis-values.yaml rediscart charts/redis
    NAME: rediscart
    LAST DEPLOYED: Fri Aug 21 15:48:51 2026
    NAMESPACE: default
    STATUS: pending-install
    REVISION: 1
    DESCRIPTION: Dry run complete

</details>

******

<details>
<summary>Demo Project: Deploy Microservices with Helmfile</summary>
 <br />

### Demo Executed: From helm install scripts to Helmfile

#### Deployed Microservices Application with "helm install"
`install.sh` runs one `helm install` per service with its values file:

    root@PC:~/k8s/microservices# cat install.sh
    helm install -f values/redis-values.yaml rediscart charts/redis
    
    helm install -f values/email-service-values.yaml emailservice charts/microservice
    helm install -f values/cart-service-values.yaml cartservice charts/microservice
    helm install -f values/currency-service-values.yaml currencyservice charts/microservice
    helm install -f values/payment-service-values.yaml paymentservice charts/microservice
    helm install -f values/recommendation-service-values.yaml recommendationservice charts/microservice
    helm install -f values/productcatalog-service-values.yaml productcatalogservice charts/microservice
    helm install -f values/shipping-service-values.yaml shippingservice charts/microservice
    helm install -f values/ad-service-values.yaml adservice charts/microservice
    helm install -f values/checkout-service-values.yaml checkoutservice charts/microservice
    helm install -f values/frontend-values.yaml frontendservice charts/microservice

Ran it, then removed all releases with `uninstall.sh`:

    root@PC:~/k8s/microservices# chmod u+x install.sh
    root@PC:~/k8s/microservices# ./install.sh
    NAME: rediscart
    LAST DEPLOYED: Fri Aug 21 15:57:39 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    DESCRIPTION: Install complete
    ...
    NAME: frontendservice
    LAST DEPLOYED: Fri Aug 21 15:57:42 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    
    root@PC:~/k8s/microservices# ./uninstall.sh
    release "rediscart" uninstalled
    release "emailservice" uninstalled
    ...
    release "frontendservice" uninstalled

#### Installed Helmfile
Downloaded the Linux release of Helmfile, extracted it and moved the binary to `/usr/local/bin`:

    root@PC:~/k8s/microservices# wget https://github.com/helmfile/helmfile/releases/download/v0.164.0/helmfile_0.164.0_linux_amd64.tar.gz
    
    root@PC:~/k8s/microservices# tar -zxvf helmfile_0.164.0_linux_amd64.tar.gz
    LICENSE
    README-zh_CN.md
    README.md
    helmfile
    
    root@PC:~/k8s/microservices# chmod +x helmfile
    root@PC:~/k8s/microservices# mv helmfile /usr/local/bin/
    
    root@PC:~/k8s/microservices# helmfile --version
    helmfile version 0.164.0

#### Created Helmfile
`helmfile.yaml` lists every release with its chart and values file. For `rediscart`, two values are overridden inline:

    root@PC:~/k8s/microservices# cat helmfile.yaml
    releases:
      - name: rediscart
        chart: charts/redis
        values:
          - values/redis-values.yaml
          - appReplicas: "1"
          - volumeName: "redis-cart-data"
    
      - name: emailservice
        chart: charts/microservice
        values:
          - values/email-service-values.yaml
    
      - name: cartservice
        chart: charts/microservice
        values:
          - values/cart-service-values.yaml
    
      - name: currencyservice
        chart: charts/microservice
        values:
          - values/currency-service-values.yaml
    
      - name: paymentservice
        chart: charts/microservice
        values:
          - values/payment-service-values.yaml
    
      - name: recommendationservice
        chart: charts/microservice
        values:
          - values/recommendation-service-values.yaml
    
      - name: productcatalogservice
        chart: charts/microservice
        values:
          - values/productcatalog-service-values.yaml
    
      - name: shippingservice
        chart: charts/microservice
        values:
          - values/shipping-service-values.yaml
    
      - name: adservice
        chart: charts/microservice
        values:
          - values/ad-service-values.yaml
    
      - name: checkoutservice
        chart: charts/microservice
        values:
          - values/checkout-service-values.yaml
    
      - name: frontendservice
        chart: charts/microservice
        values:
          - values/frontend-values.yaml

#### Deployed Helm Charts with Helmfile
Deployed all releases with `helmfile sync`:

    root@PC:~/k8s/microservices# helmfile sync
    Building dependency release=rediscart, chart=charts/redis
    Building dependency release=cartservice, chart=charts/microservice
    ...
    UPDATED RELEASES:
    NAME                    NAMESPACE   CHART                 VERSION   DURATION
    checkoutservice                     charts/microservice   0.1.0     2s
    recommendationservice               charts/microservice   0.1.0     2s
    ...

Checked the releases and the pods:

    root@PC:~/k8s/microservices# helmfile list
    NAME                    NAMESPACE       ENABLED INSTALLED       LABELS  CHART                   VERSION
    rediscart                               true    true                    charts/redis
    emailservice                            true    true                    charts/microservice
    ...
    
    root@PC:~/k8s/microservices# kubectl get pod
    NAME                                     READY   STATUS    RESTARTS   AGE
    adservice-5f8b8889c9-jzgmv               1/1     Running   0          46s
    cartservice-548cc667f7-8tfrw             1/1     Running   0          47s
    ...

Removed everything with `helmfile destroy`:

    root@PC:~/k8s/microservices# helmfile destroy
    Building dependency release=frontendservice, chart=charts/microservice
    ...
    Deleting frontendservice
    Deleting checkoutservice
    ...
    DELETED RELEASES:
    NAME                    NAMESPACE   DURATION
    recommendationservice               0s
    cartservice                         0s
    ...

</details>

******
