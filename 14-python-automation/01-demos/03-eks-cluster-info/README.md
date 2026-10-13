# Automate displaying EKS cluster information

**Technologies:** Python, Boto3, AWS EKS

I created an EKS cluster with Terraform and wrote a Python script that prints the status and details of all EKS clusters in the region.

## Summary
- `terraform/vpc.tf` creates the VPC with the `terraform-aws-modules/vpc/aws` module (private and public subnets, one NAT gateway).
- `terraform/eks-cluster.tf` creates `myapp-eks-cluster` (Kubernetes 1.33) with the `terraform-aws-modules/eks/aws` module and a managed node group of 3 `t2.small` nodes.
- `eks-check.py` gets all clusters in `eu-central-1` with `list_clusters()`, then calls `describe_cluster()` for each one and prints the status, API endpoint and Kubernetes version.

## Run
```bash
cd terraform
terraform init
terraform apply
cd ..
pip install boto3
python eks-check.py
```

## Result
Cluster created with Terraform, then the script output for it:
```
Plan: 62 to add, 0 to change, 0 to destroy.
...
module.eks.aws_eks_cluster.this[0]: Creation complete after 10m22s [id=myapp-eks-cluster]
...
Apply complete! Resources: 62 added, 0 changed, 0 destroyed.

(.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/03-automate-display-eks/eks-check.py
Cluster myapp-eks-cluster status is ACTIVE
Cluster endpoint:https://E6719366FF375E2340E8C825A540B76C.gr7.eu-central-1.eks.amazonaws.com
Cluster version: 1.33
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
