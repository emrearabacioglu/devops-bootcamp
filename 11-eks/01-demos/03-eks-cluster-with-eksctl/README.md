# Create EKS cluster with eksctl

**Technologies:** Kubernetes, AWS EKS, Eksctl, Linux

I created an EKS cluster with a managed node group using one `eksctl` command, instead of creating the roles, VPC, cluster and node group by hand in the console.

## Summary
1. Installed the `eksctl` binary and checked with `aws configure list` that the AWS CLI has credentials and the `eu-central-1` region.
2. Ran `eksctl create cluster` for `demo-cluster` with the node group `demo-nodes` (`t2.micro`, min 1, max 3, desired 2).
3. Version 1.27 was rejected as no longer supported, so I ran it again with 1.36.
4. eksctl created two CloudFormation stacks (cluster and node group), the add-ons and the node group, and saved the kubeconfig, so `kubectl` worked right away.

This folder has no config files: the whole setup is the `eksctl` command below.

## Run
```bash
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version

eksctl create cluster --name demo-cluster --version 1.36 --region eu-central-1 --nodegroup-name demo-nodes --node-type t2.micro --nodes 2 --nodes-min 1 --nodes-max 3

kubectl get nodes
```

## Result
eksctl finishes with the cluster ready, and both nodes are `Ready`:
```
2026-09-03 13:34:00 [✔]  saved kubeconfig as "/root/.kube/config"
2026-09-03 13:34:00 [✔]  all EKS cluster resources for "demo-cluster" have been created
2026-09-03 13:34:00 [ℹ]  node "ip-192-168-26-26.eu-central-1.compute.internal" is ready
2026-09-03 13:34:00 [ℹ]  node "ip-192-168-68-99.eu-central-1.compute.internal" is ready
2026-09-03 13:34:00 [✔]  created 1 managed nodegroup(s) in cluster "demo-cluster"
2026-09-03 13:34:01 [ℹ]  creating addon: metrics-server
2026-09-03 13:34:03 [✔]  EKS cluster "demo-cluster" in "eu-central-1" region is ready
...
root@PC:~/k8s-on-aws# kubectl get nodes
NAME                                             STATUS   ROLES    AGE   VERSION
ip-192-168-26-26.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
ip-192-168-68-99.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
