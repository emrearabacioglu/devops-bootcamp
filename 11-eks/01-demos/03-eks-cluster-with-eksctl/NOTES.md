# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create EKS cluster with eksctl

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
