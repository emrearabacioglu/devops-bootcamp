# Terraform & AWS EKS

**Technologies:** Terraform, AWS EKS, Docker, Linux, Git

I created an EKS cluster with Terraform, using the VPC and EKS modules from the Terraform Registry, and deployed nginx on it to test it.

## Summary
- `vpc.tf` uses `terraform-aws-modules/vpc/aws`: a VPC with 3 private and 3 public subnets in 3 AZs, one NAT gateway, and the `kubernetes.io/...` tags that EKS and the load balancers need.
- `eks-cluster.tf` uses `terraform-aws-modules/eks/aws`: cluster `myapp-eks-cluster` (Kubernetes 1.33) in the private subnets, a managed node group `dev` with 3 `t2.small` nodes, and the CoreDNS, kube-proxy and vpc-cni add-ons.
- `terraform.tfvars` has the CIDR ranges, `providers.tf` the AWS provider version.
- `terraform apply` created 62 resources. The cluster alone took about 8 minutes.
- Connected kubectl with `aws eks update-kubeconfig` and applied `nginx-config.yaml` (nginx Deployment + Service of type `LoadBalancer`).
- `terraform destroy` first failed with `DependencyViolation`: the load balancer that Kubernetes created for the nginx Service is not in the Terraform state, so the VPC could not be deleted. I removed the leftovers in the AWS console and ran `terraform destroy` again. Lesson: delete the K8s Service before destroying the cluster.

## Run
```bash
terraform init
terraform apply --auto-approve
aws eks update-kubeconfig --name myapp-eks-cluster --region eu-central-1
kubectl get node
kubectl apply -f nginx-config.yaml
kubectl get svc
```

## Result
Cluster created, 3 nodes `Ready`, and nginx reachable through an AWS load balancer:
```
Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
...
root@PC:~/modules/terraform (feature/eks)# kubectl get node
NAME                                          STATUS   ROLES    AGE   VERSION
ip-10-0-1-175.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
ip-10-0-2-147.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
ip-10-0-3-48.eu-central-1.compute.internal    Ready    <none>   50m   v1.33.13-eks-cb19647
...
root@PC:~/modules/terraform (feature/eks)# kubectl get svc
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
kubernetes   ClusterIP      172.20.0.1     <none>                                                                   443/TCP        71m
nginx        LoadBalancer   172.20.3.243   a9e4950619e104317bd888cf6839b22f-825226598.eu-central-1.elb.amazonaws.com   80:31956/TCP   12m
```

Commit history: branch `feature/eks` in my [terraform](https://github.com/emrearabacioglu/terraform) repo.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
