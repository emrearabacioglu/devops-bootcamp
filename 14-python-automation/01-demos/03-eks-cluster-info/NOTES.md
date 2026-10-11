# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate displaying EKS cluster information

### Demo Executed: Displaying EKS Cluster Information with Boto3

#### Preparation: EKS Cluster with Terraform
Created an EKS cluster with the official Terraform registry modules: the VPC module (same setup as in the Terraform module) and the EKS module with a managed node group of 3 `t2.small` nodes.

```hcl
    module "eks" {
      source  = "terraform-aws-modules/eks/aws"
      version = "21.25.0"

      name               = "myapp-eks-cluster"
      kubernetes_version = "1.33"

      subnet_ids = module.myapp-vpc.private_subnets
      vpc_id     = module.myapp-vpc.vpc_id

      endpoint_public_access                   = true
      enable_cluster_creator_admin_permissions = true

      addons = {
        coredns                = {}
        eks-pod-identity-agent = {
          before_compute = true
        }
        kube-proxy             = {}
        vpc-cni                = {
          before_compute = true
        }
      }

      eks_managed_node_groups = {
        dev = {
          ami_type       = "AL2023_x86_64_STANDARD"
          instance_types = ["t2.small"]

          min_size     = 1
          max_size     = 3
          desired_size = 3
        }
      }

      tags = {
        environment = "development"
        application = "myapp"
      }
    }
```

Applied the configuration:
```bash
    root@PC:~/modules/python-automation/03-automate-display-eks/terraform# terraform apply
    ...
    Plan: 62 to add, 0 to change, 0 to destroy.
    ...
    module.eks.aws_eks_cluster.this[0]: Creation complete after 10m22s [id=myapp-eks-cluster]
    ...
    module.eks.module.eks_managed_node_group["dev"].aws_eks_node_group.this[0]: Creation complete after 1m50s [id=myapp-eks-cluster:dev-bcd8951e7992956431dc8f3880]
    ...
    Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
```

#### Cluster Information Script
The script lists all EKS clusters in the region with `list_clusters()` and gets the details of each cluster with `describe_cluster()`: status, API endpoint and Kubernetes version.

```python
    import boto3

    client = boto3.client('eks', region_name="eu-central-1")
    clusters = client.list_clusters()['clusters']

    for cluster in clusters:
        response = client.describe_cluster(
            name=cluster
        )
        cluster_info = response['cluster']
        cluster_status = cluster_info['status']
        cluster_endpoint = cluster_info['endpoint']
        cluster_version = cluster_info['version']
        print(f"Cluster {cluster} status is {cluster_status}\nCluster endpoint:{cluster_endpoint}\nCluster version: {cluster_version}")
```

#### Execution
Status, endpoint and version of the new cluster:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/03-automate-display-eks/eks-check.py
    Cluster myapp-eks-cluster status is ACTIVE
    Cluster endpoint:https://E6719366FF375E2340E8C825A540B76C.gr7.eu-central-1.eks.amazonaws.com
    Cluster version: 1.33
```
