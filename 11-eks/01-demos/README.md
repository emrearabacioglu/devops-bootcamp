# Module 11 – Kubernetes on AWS - EKS

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Create AWS EKS cluster with a Node Group | IAM roles, VPC, cluster and node group from the console; Cluster Autoscaler scaling the node group up and down |
| 2 | Create EKS cluster with Fargate profile | Pod execution role, Fargate profile for the `dev` namespace, nginx pods on Fargate nodes |
| 3 | Create EKS cluster with eksctl | One `eksctl create cluster` command for the cluster and a managed node group |
| 4 | CD - Deploy to EKS cluster from Jenkins Pipeline | kubectl and aws-iam-authenticator in the Jenkins container, kubeconfig, deploy nginx from a pipeline |
| 5 | Complete CI/CD Pipeline with EKS and private DockerHub registry | `envsubst` manifests, registry secret, version bump → build → push → deploy → commit |
| 6 | Complete CI/CD Pipeline with EKS and AWS ECR | Same pipeline with ECR as the registry |

## Takeaways

- **kubeconfig for EKS:** `aws eks update-kubeconfig --name <cluster>` adds the cluster context to `~/.kube/config`. The user entry runs `aws eks get-token` to authenticate.
- **Console setup order:** EKS cluster role → VPC (CloudFormation template) → cluster → node group role → node group.
- **Cluster Autoscaler permissions:** a custom IAM policy with `autoscaling` and `ec2` permissions, attached to the node group role.
- **Annotation error:** `cannot unmarshal string into Go struct field ObjectMeta.metadata.annotations of type map[string]string` came from the ServiceAccount annotation in `cluster-autoscaler-autodiscover.yaml` (it's written as `role-arn:arn:...`, without a space after the colon). Fixed the file and applied it again.
- **Autoscaling in action:** scaling nginx to 20 replicas left pods `Pending`, the autoscaler logged `TriggeredScaleUp ... 1->3 (max: 3)` and added 2 nodes. After scaling down, the extra nodes went `Ready,SchedulingDisabled` and were then removed.
- **`type: LoadBalancer` on EKS:** creates an AWS load balancer; its DNS name shows up as `EXTERNAL-IP` in `kubectl get svc`.
- **Fargate:** needs a pod execution role and a Fargate profile (here namespace `dev` + label `profile: fargate`). Matching pods start `Pending` for about a minute, then each one runs on its own `fargate-ip-...` node.
- **eksctl:** one command creates the CloudFormation stacks, cluster, node group and kubeconfig. `--version 1.27` failed because it's no longer supported; 1.36 worked.
- **Jenkins → EKS:** install `kubectl` and `aws-iam-authenticator` inside the Jenkins container (`docker exec -u 0`), copy the kubeconfig to `/var/jenkins_home/.kube/`, and pass the AWS keys as `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` with `credentials()` in the deploy stage.
- **envsubst:** comes with `gettext-base`. `envsubst < kubernetes/deployment.yaml | kubectl apply -f -` fills `$APP_NAME` and `$IMAGE_NAME` from the pipeline environment.
- **Private registry pulls:** `kubectl create secret docker-registry <name> ...` and `imagePullSecrets` in the deployment. For ECR the username is `AWS` and the password is the ECR token.
- **t2.micro pod limit:** pods stayed `Pending` with `0/2 nodes are available: 2 Too many pods` because of the ENI limit on t2.micro nodes.

******

<details>
<summary>Demo Project: Create AWS EKS cluster with a Node Group</summary>
 <br />

### Demo Executed: Part 1 – EKS cluster and node group from the AWS console

#### IAM Roles, VPC and Cluster
Created the EKS cluster role, which gives the control plane its permissions:

<img width="1698" height="833" alt="image" src="https://github.com/user-attachments/assets/46aa3448-e58d-4707-be12-49ac1be7bc49" />
<img width="1698" height="529" alt="image" src="https://github.com/user-attachments/assets/dc619f96-ca96-4939-97f1-ab04a9fcd394" />

Created a VPC for the cluster from a CloudFormation template:

<img width="1698" height="589" alt="image" src="https://github.com/user-attachments/assets/b6e1a7fd-774a-4de2-9934-3598d827c965" />

Created the EKS cluster (`eks-cluster-test`):

<img width="1708" height="835" alt="image" src="https://github.com/user-attachments/assets/1c6c455b-96f0-477b-850b-e3c1f9bdc398" />

Created the node group role for the EC2 worker nodes:

<img width="1698" height="667" alt="image" src="https://github.com/user-attachments/assets/c03d8c59-31a6-472b-98b2-4af763e31534" />

Created the node group (EC2 instances that act as worker nodes):

<img width="1700" height="627" alt="image" src="https://github.com/user-attachments/assets/64f0f2a9-ba86-4734-a596-9a14d88618c7" />

#### Local kubeconfig
Checked the AWS CLI config and added the cluster to the local kubeconfig:
```bash
    root@PC:~/k8s-on-aws# aws configure list
    NAME       : VALUE                    : TYPE             : LOCATION
    profile    : <not set>                : None             : None
    access_key : ****************UJWN     : shared-credentials-file :
    secret_key : ****************7sE6     : shared-credentials-file :
    region     : eu-central-1             : config-file      : ~/.aws/config

    root@PC:~/k8s-on-aws# aws eks update-kubeconfig --name eks-cluster-test
    Added new context arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test to /root/.kube/config
```
The kubeconfig now has the EKS cluster next to minikube, and it's the current context:
```bash
    root@PC:~/k8s-on-aws# cat /root/.kube/config
    apiVersion: v1
    clusters:
    - cluster:
        certificate-authority: /root/.minikube/ca.crt
        extensions:
        - extension:
            last-update: Fri, 21 Aug 2026 15:11:57 +03
            provider: minikube.sigs.k8s.io
            version: v1.38.1
          name: cluster_info
        server: https://127.0.0.1:62471
      name: minikube
    - cluster:
        certificate-authority-data: ***
        server: https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com
      name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    contexts:
    - context:
        cluster: minikube
        extensions:
        - extension:
            last-update: Fri, 21 Aug 2026 15:11:57 +03
            provider: minikube.sigs.k8s.io
            version: v1.38.1
          name: context_info
        namespace: default
        user: minikube
      name: minikube
    - context:
        cluster: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
        user: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
      name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    current-context: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    kind: Config
    users:
    - name: minikube
      user:
        client-certificate: /root/.minikube/profiles/minikube/client.crt
        client-key: /root/.minikube/profiles/minikube/client.key
    - name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
      user:
        exec:
          apiVersion: client.authentication.k8s.io/v1beta1
          args:
          - --region
          - eu-central-1
          - eks
          - get-token
          - --cluster-name
          - eks-cluster-test
          - --output
          - json
          command: aws
```

#### Cluster Access Check
kubectl can reach the cluster. Namespaces, control plane and CoreDNS:
```bash
    root@PC:~/k8s-on-aws# kubectl get namespaces
    NAME               STATUS   AGE
    default            Active   53m
    external-dns       Active   50m
    kube-node-lease    Active   53m
    kube-public        Active   53m
    kube-system        Active   53m

    root@PC:~/k8s-on-aws# kubectl cluster-info
    Kubernetes control plane is running at https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com
    CoreDNS is running at https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

#### Worker Nodes
Both EC2 instances joined the cluster and are `Ready`:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                              STATUS   ROLES    AGE    VERSION
    ip-192-168-223-47.eu-central-1.compute.internal   Ready    <none>   3m8s   v1.36.3-eks-cb19647
    ip-192-168-61-45.eu-central-1.compute.internal    Ready    <none>   3m4s   v1.36.3-eks-cb19647
```

### Demo Executed: Part 2 – Autoscaling

#### IAM Policy for the Autoscaler
The Cluster Autoscaler changes the desired capacity of the node group's Auto Scaling Group, so it needs IAM permissions.

Created a custom IAM policy with the `autoscaling` and `ec2` permissions:

<img width="1700" height="529" alt="image" src="https://github.com/user-attachments/assets/e298cd7d-c3b4-4d05-b945-ea585503b5f7" />
<img width="1682" height="833" alt="image" src="https://github.com/user-attachments/assets/7c28ac5b-58ba-4ccc-8921-5b99094c96ff" />
<img width="1692" height="759" alt="image" src="https://github.com/user-attachments/assets/5591dd32-f5ec-4314-8dbd-0a1ae241b6da" />

Attached the policy to the existing node group role:

<img width="1694" height="809" alt="image" src="https://github.com/user-attachments/assets/17fe26bd-78bc-4f1d-96c8-1f0e3d8d482c" />
<img width="1712" height="607" alt="image" src="https://github.com/user-attachments/assets/90c604a0-4882-4e26-93e9-56bcf45b1db9" />
<img width="1700" height="695" alt="image" src="https://github.com/user-attachments/assets/ee1f0128-b909-40ba-b6fb-b8e7e182af6d" />

#### Cluster Autoscaler Deployment
Applied `cluster-autoscaler-autodiscover.yaml`. The first apply failed on the ServiceAccount annotation (YAML error). After fixing it, the second apply created the ServiceAccount and the autoscaler pod started:
```bash
    root@PC:~/k8s-on-aws# cat cluster-autoscaler-autodiscover.yaml
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      labels:
        k8s-addon: cluster-autoscaler.addons.k8s.io
        k8s-app: cluster-autoscaler
      name: cluster-autoscaler
      namespace: kube-system
      annotations:
        eks.amazonaws.com/role-arn:arn:aws:iam::731872836472:role/EKSServiceAccountRole
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: cluster-autoscaler
      labels:
        k8s-addon: cluster-autoscaler.addons.k8s.io
        k8s-app: cluster-autoscaler
    rules:
      - apiGroups: [""]
        resources: ["events", "endpoints"]
        verbs: ["create", "patch"]
    ... [Truncated for brevity] ...
    
    root@PC:~/k8s-on-aws# kubectl apply -f cluster-autoscaler-autodiscover.yaml
    clusterrole.rbac.authorization.k8s.io/cluster-autoscaler created
    ...
    error: unable to decode "cluster-autoscaler-autodiscover.yaml": json: cannot unmarshal string into Go struct field ObjectMeta.metadata.annotations of type map[string]string
    
    root@PC:~/k8s-on-aws# kubectl apply -f cluster-autoscaler-autodiscover.yaml
    serviceaccount/cluster-autoscaler created
    clusterrole.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    role.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    clusterrolebinding.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    rolebinding.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    deployment.apps/cluster-autoscaler unchanged
    
    root@PC:~/k8s-on-aws# kubectl get pod -n kube-system
    NAME                                 READY   STATUS    RESTARTS   AGE
    aws-node-7qbqs                       2/2     Running   0          173m
    cluster-autoscaler-fb4856648-qj8xr   1/1     Running   0          57s
    coredns-c4b9957df-k7n97              1/1     Running   0          16h
```

#### Nginx with a LoadBalancer Service
Deployed nginx with a `type: LoadBalancer` service. AWS created a load balancer and its DNS name is the `EXTERNAL-IP`:
```bash
    root@PC:~/k8s-on-aws# cat nginx-config.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
    spec:
      selector:
        matchLabels:
          app: nginx
      replicas: 1
      template:
        metadata:
          labels:
            app: nginx
        spec:
          containers:
          - name: nginx
            image: nginx
            ports:
            - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      ports:
      - name: http
        port: 80
        protocol: TCP
        targetPort: 80
      selector:
        app: nginx
      type: LoadBalancer
      
    root@PC:~/k8s-on-aws# kubectl apply -f nginx-config.yaml
    deployment.apps/nginx created
    service/nginx created
    
    root@PC:~/k8s-on-aws# kubectl get svc
    NAME         TYPE           CLUSTER-IP       EXTERNAL-IP                                                               PORT(S)        AGE
    kubernetes   ClusterIP      10.100.0.1       <none>                                                                    443/TCP        19h
    nginx        LoadBalancer   10.100.190.149   a4d6933ade5dd4ec39879d432e7de9d9-1736632215.eu-central-1.elb.amazonaws.com   80:30823/TCP   27s
```
<img width="1700" height="825" alt="image" src="https://github.com/user-attachments/assets/96cee4d3-9f84-416e-84a9-443603ec2e07" />
<img width="1706" height="403" alt="image" src="https://github.com/user-attachments/assets/d5d499af-7cc2-41eb-9ec1-fd470b88a2d5" />

#### Scaling Up and Down
Changed the nginx deployment to 20 replicas. The new pods were `Pending` because the node didn't have enough resources:
```bash
    root@PC:~/k8s-on-aws# kubectl edit deployment nginx
    deployment.apps/nginx edited
    
    root@PC:~/k8s-on-aws# kubectl get pod
    NAME                     READY   STATUS    RESTARTS   AGE
    nginx-5cf8dc6bc5-277m6   0/1     Pending   0          9s
    nginx-5cf8dc6bc5-2h9bn   0/1     Pending   0          9s
    nginx-5cf8dc6bc5-2wtmp   1/1     Running   0          21m
    nginx-5cf8dc6bc5-56zbl   0/1     Pending   0          9s
    ...
```
Cluster Autoscaler logs: it saw the unschedulable pods and set the node group size from 1 to 3:
```bash
    I0902 12:04:23.513273        1 static_autoscaler.go:569] Unschedulable pods are very new, waiting one iteration for more
    I0902 12:04:34.098520        1 orchestrator.go:120] Upcoming 2 nodes
    I0902 12:04:33.899713        1 executor.go:166] Scale-up: setting group eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 size to 3
    I0902 12:04:34.087353        1 event_sink_logging_wrapper.go:48] Event(v1.ObjectReference{Kind:"Pod", Namespace:"default", Name:"nginx-5cf8dc6bc5-k9k52" ... reason: 'TriggeredScaleUp' pod triggered scale-up: [{eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 1->3 (max: 3)}]
```
The two new nodes joined and are `Ready`:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                               STATUS   ROLES    AGE     VERSION
    ip-192-168-195-122.eu-central-1.compute.internal   Ready    <none>   2m26s   v1.36.3-eks-cb19647
    ip-192-168-208-204.eu-central-1.compute.internal   Ready    <none>   2m22s   v1.36.3-eks-cb19647
    ip-192-168-51-213.eu-central-1.compute.internal    Ready    <none>   3h46m   v1.36.3-eks-cb19647
```
After scaling the deployment back down, the extra nodes were cordoned (`SchedulingDisabled`) and then removed:
```bash
    root@PC:~/k8s-on-aws# kubectl get node
    NAME                                               STATUS                     ROLES    AGE   VERSION
    ip-192-168-195-122.eu-central-1.compute.internal   Ready,SchedulingDisabled   <none>   15m   v1.36.3-eks-cb19647
    ip-192-168-208-204.eu-central-1.compute.internal   Ready,SchedulingDisabled   <none>   15m   v1.36.3-eks-cb19647
    ip-192-168-51-213.eu-central-1.compute.internal    Ready                      <none>   4h    v1.36.3-eks-cb19647
    
    root@PC:~/k8s-on-aws# kubectl get node
    NAME                                              STATUS   ROLES    AGE    VERSION
    ip-192-168-51-213.eu-central-1.compute.internal   Ready    <none>   4h1m   v1.36.3-eks-cb19647
```

</details>

******

<details>
<summary>Demo Project: Create EKS cluster with Fargate profile</summary>
 <br />

### Demo Executed: Run nginx pods on Fargate

#### Pod Execution Role and Fargate Profile
Created an EKS pod execution role. Fargate uses it to pull images and run the pods:

<img width="1692" height="821" alt="image" src="https://github.com/user-attachments/assets/2c5a62b3-6016-4b60-b461-0c6c15329371" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/d1fa5fd5-bbb3-4f78-996b-9f05966eee81" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/9c97736e-5c02-4c43-983c-7a0834ccfff0" />

Created a Fargate profile for the `dev` namespace with the selector `profile: fargate`. Pods that match it run on Fargate instead of the EC2 node group:

<img width="1694" height="801" alt="image" src="https://github.com/user-attachments/assets/38ddab5a-aeb3-4bc5-8afc-428a04e9ebfd" />
<img width="1708" height="689" alt="image" src="https://github.com/user-attachments/assets/720afcfd-4bd0-47df-b8e2-e709c85882d6" />
<img width="1706" height="601" alt="image" src="https://github.com/user-attachments/assets/f5ad4eee-d27e-4bd2-93a2-eeab50e0c77e" />
<img width="1690" height="799" alt="image" src="https://github.com/user-attachments/assets/8e65ff03-f43f-4dbb-b6b7-61c7573798ea" />

#### Deploying to Fargate
The nginx manifest uses namespace `dev` and the `profile: fargate` label to match the profile:
```bash
    root@PC:~/k8s-on-aws# cat nginx-config.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
      namespace: dev
      labels:
        app: nginx
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: nginx
          profile: fargate
    template:
      metadata:
        labels:
          app: nginx
          profile: fargate
      spec:
        containers:
        - name: nginx
          image: nginx
          ports:
          - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      ports:
      - name: http
        port: 80
        protocol: TCP
        targetPort: 80
      selector:
        app: nginx
      type: LoadBalancer
```
Created the `dev` namespace and applied the manifest:
```bash
    root@PC:~/k8s-on-aws# kubectl get ns
    NAME              STATUS   AGE
    default           Active   21h
    external-dns      Active   21h
    kube-node-lease   Active   21h
    kube-public       Active   21h
    kube-system       Active   21h
    
    root@PC:~/k8s-on-aws# kubectl create ns dev
    namespace/dev created
    
    root@PC:~/k8s-on-aws# kubectl apply -f nginx-config.yaml
    deployment.apps/nginx created
    service/nginx unchanged
```
Watched the pods. They stayed `Pending` for about a minute while Fargate started the compute for them, then went to `Running`:
```bash
    root@PC:~/k8s-on-aws# kubectl get pods -n dev -w
    NAME                    READY   STATUS    RESTARTS   AGE
    nginx-fd684dfd4-p8jpq   0/1     Pending   0          33s
    nginx-fd684dfd4-vs9zt   0/1     Pending   0          33s
    nginx-fd684dfd4-vs9zt   0/1     Pending   0          51s
    nginx-fd684dfd4-vs9zt   0/1     ContainerCreating   0          52s
    nginx-fd684dfd4-vs9zt   0/1     ContainerCreating   0          52s
    nginx-fd684dfd4-vs9zt   1/1     Running             0          58s
    nginx-fd684dfd4-p8jpq   0/1     Pending             0          59s
    nginx-fd684dfd4-p8jpq   0/1     ContainerCreating   0          59s
    nginx-fd684dfd4-p8jpq   0/1     ContainerCreating   0          60s
    nginx-fd684dfd4-p8jpq   1/1     Running             0          66s
```
Two Fargate nodes appeared next to the existing EC2 node:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                                      STATUS   ROLES    AGE     VERSION
    fargate-ip-192-168-152-97.eu-central-1.compute.internal   Ready    <none>   6m48s   v1.36.2-eks-254016e
    fargate-ip-192-168-165-70.eu-central-1.compute.internal   Ready    <none>   6m56s   v1.36.2-eks-254016e
    ip-192-168-51-213.eu-central-1.compute.internal           Ready    <none>   5h47m   v1.36.3-eks-cb19647
```

</details>

******

<details>
<summary>Demo Project: Create EKS cluster with eksctl</summary>
 <br />

### Demo Executed: Create a cluster and node group with one eksctl command

#### eksctl Installation
Installed the `eksctl` binary and checked that the AWS CLI has credentials and the `eu-central-1` region:
```bash
    root@PC:~/k8s-on-aws# curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
    root@PC:~/k8s-on-aws# sudo mv /tmp/eksctl /usr/local/bin
    root@PC:~/k8s-on-aws# eksctl version
    0.230.0
    root@PC:~/k8s-on-aws# aws configure list
    NAME       : VALUE                      : TYPE             : LOCATION
    profile    : <not set>                  : None             : None
    access_key : ****************UJWN       : shared-credentials-file :
    secret_key : ****************7sE6       : shared-credentials-file :
    region     : eu-central-1               : config-file      : ~/.aws/config
```

#### Cluster Creation
Created `demo-cluster` with a managed node group `demo-nodes` (`t2.micro`, min 1, max 3, desired 2). Version 1.27 was rejected as no longer supported, so I ran it again with 1.36. eksctl created the CloudFormation stacks, the add-ons and the node group, and saved the kubeconfig:
```bash
    root@PC:~/k8s-on-aws# eksctl create cluster \
    > --name demo-cluster \
    > --version 1.27 \
    > --region eu-central-1 \
    > --nodegroup-name demo-nodes \
    > --node-type t2.micro \
    > --nodes 2 \
    > --nodes-min 1 \
    > --nodes-max 3
    Error: resolving cluster version: invalid version, 1.27 is no longer supported, supported values: 1.31, 1.32, 1.33, 1.34, 1.35, 1.36
    see also: https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
    
    root@PC:~/k8s-on-aws# eksctl create cluster --name demo-cluster --version 1.36 --region eu-central-1 --nodegroup-name demo-nodes --node-type t2.micro --nodes 2 --nodes-min 1 --nodes-max 3
    2026-09-03 13:21:37 [ℹ]  eksctl version 0.230.0
    2026-09-03 13:21:37 [ℹ]  using region eu-central-1
    2026-09-03 13:21:38 [ℹ]  setting availability zones to [eu-central-1a eu-central-1b eu-central-1c]
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1a - public:192.168.0.0/19 private:192.168.96.0/19
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1b - public:192.168.32.0/19 private:192.168.128.0/19
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1c - public:192.168.64.0/19 private:192.168.160.0/19
    2026-09-03 13:21:38 [ℹ]  nodegroup "demo-nodes" will use "" [AmazonLinux2023/1.36]
    2026-09-03 13:21:38 [ℹ]  using Kubernetes version 1.36
    2026-09-03 13:21:38 [ℹ]  creating EKS cluster "demo-cluster" in "eu-central-1" region with managed nodes
    2026-09-03 13:21:38 [ℹ]  will create 2 separate CloudFormation stacks for cluster itself and the initial managed nodegroup
    ...
    2026-09-03 13:21:38 [ℹ]  deploying stack "eksctl-demo-cluster-cluster"
    2026-09-03 13:22:08 [ℹ]  waiting for CloudFormation stack "eksctl-demo-cluster-cluster"
    ...
    2026-09-03 13:29:42 [ℹ]  creating addon: kube-proxy
    2026-09-03 13:29:42 [ℹ]  successfully created addon: kube-proxy
    2026-09-03 13:29:43 [ℹ]  creating addon: coredns
    2026-09-03 13:29:43 [ℹ]  successfully created addon: coredns
    ...
    2026-09-03 13:31:46 [ℹ]  deploying stack "eksctl-demo-cluster-nodegroup-demo-nodes"
    2026-09-03 13:31:46 [ℹ]  waiting for CloudFormation stack "eksctl-demo-cluster-nodegroup-demo-nodes"
    ...
    2026-09-03 13:34:00 [✔]  saved kubeconfig as "/root/.kube/config"
    2026-09-03 13:34:00 [✔]  all EKS cluster resources for "demo-cluster" have been created
    2026-09-03 13:34:00 [ℹ]  node "ip-192-168-26-26.eu-central-1.compute.internal" is ready
    2026-09-03 13:34:00 [ℹ]  node "ip-192-168-68-99.eu-central-1.compute.internal" is ready
    2026-09-03 13:34:00 [✔]  created 1 managed nodegroup(s) in cluster "demo-cluster"
    2026-09-03 13:34:01 [ℹ]  creating addon: metrics-server
    2026-09-03 13:34:03 [✔]  EKS cluster "demo-cluster" in "eu-central-1" region is ready
```

#### Verification
Both nodes are `Ready`. No pods in the default namespace yet:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                             STATUS   ROLES    AGE   VERSION
    ip-192-168-26-26.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
    ip-192-168-68-99.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
    
    root@PC:~/k8s-on-aws# kubectl get pod
    No resources found in default namespace.
```

#### AWS Console Check
The CloudFormation stacks, VPC, EKS cluster and node group eksctl created, as seen in the console:

<img width="1682" height="703" alt="image" src="https://github.com/user-attachments/assets/c9f66985-f3ed-4dcb-8ef0-72cafceee987" />
<img width="1710" height="831" alt="image" src="https://github.com/user-attachments/assets/11f22199-d010-458f-89a1-59fda926151f" />
<img width="1712" height="587" alt="image" src="https://github.com/user-attachments/assets/b07aecad-5d3b-4837-906c-05d3f4cbcd3c" />
<img width="1696" height="801" alt="image" src="https://github.com/user-attachments/assets/9b18ad68-c292-4ac2-975e-32bd1b416085" />
<img width="1694" height="823" alt="image" src="https://github.com/user-attachments/assets/e217309b-0775-4e09-a692-7d02217c810a" />

</details>

******

<details>
<summary>Demo Project: CD - Deploy to EKS cluster from Jenkins Pipeline</summary>
 <br />

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

</details>

******

<details>
<summary>Demo Project: Complete CI/CD Pipeline with EKS and private DockerHub registry</summary>
 <br />

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

</details>

******

<details>
<summary>Demo Project: Complete CI/CD Pipeline with EKS and AWS ECR</summary>
 <br />

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

</details>

******
