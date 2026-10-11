# Automate Kubernetes Deployment

**Technologies:** Ansible, Terraform, Kubernetes, AWS EKS, Python, Linux

I created an EKS cluster with Terraform and wrote an Ansible playbook that creates a new namespace in the cluster and deploys an nginx app into it.

## Summary
1. `terraform/vpc.tf` and `terraform/eks-cluster.tf` (the configuration from the Terraform module) create a VPC with public and private subnets, the EKS cluster `myapp-eks-cluster` and a managed node group with 3 worker nodes. The subnet CIDRs are in `terraform/terraform.tfvars.example`.
2. Generated a kubeconfig for the cluster with `aws eks update-kubeconfig` into the project folder instead of `~/.kube/config` (`kubeconfig_*` files are in `.gitignore`).
3. `deploy-to-k8s.yaml` runs on `localhost`: the `kubernetes.core.k8s` module talks to the Kubernetes API from my machine, there is no SSH to the nodes.
   - The first task creates the `my-app` namespace.
   - The second task applies `nginx-config.yaml` (nginx Deployment and LoadBalancer Service) into that namespace.
4. Set the `K8S_AUTH_KUBECONFIG` environment variable, so the playbook doesn't need a `kubeconfig` parameter in each task.

## Run
```bash
aws eks update-kubeconfig --region eu-central-1 --name myapp-eks-cluster --kubeconfig ~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
export K8S_AUTH_KUBECONFIG=~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
ansible-playbook deploy-to-k8s.yaml
```

## Result
The namespace, the nginx pod and the LoadBalancer service in the cluster:
```
root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get ns
NAME              STATUS   AGE
...
my-app            Active   2m52s

root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get pod -n my-app
NAME                     READY   STATUS    RESTARTS   AGE
nginx-86c57bc6b8-4sv2f   1/1     Running   0          22s

root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get svc -n my-app
NAME    TYPE           CLUSTER-IP       EXTERNAL-IP                                                                  PORT(S)        AGE
nginx   LoadBalancer   172.20.230.120   a18b2faca56504aabb0b7821092280a2-2021946624.eu-central-1.elb.amazonaws.com   80:32464/TCP   38s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
