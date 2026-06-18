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
 
 **content will be here**
 
</details>


******

<details>
<summary>Introduction to YAML Configuration File</summary>
 <br />
 
 **content will be here**
 
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
