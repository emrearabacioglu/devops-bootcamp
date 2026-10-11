# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Terraform & AWS EKS

### Demo Executed: Create an EKS cluster with Terraform and deploy nginx

#### Created the VPC by using the VPC module
Used the `terraform-aws-modules/vpc/aws` module: public and private subnets across multiple AZs, one NAT gateway, and the `kubernetes.io/...` tags that the cluster and load balancers need:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat vpc.tf
    ...
    module "myapp-vpc" {
      source  = "terraform-aws-modules/vpc/aws"
      version = "6.7.2"
    
      name = "myapp-vpc"
      cidr = var.vpc_cidr_block
      private_subnets = var.private_subnet_cidr_blocks
      public_subnets = var.public_subnet_cidr_blocks
      azs = data.aws_availability_zones.azs.names
    
      enable_nat_gateway = true
      single_nat_gateway = true
      enable_dns_hostnames = true
    
      tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
      }
    
      public_subnet_tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
        "kubernetes.io/role/elb" = 1
      }
    
      private_subnet_tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
        "kubernetes.io/role/internal-elb" = 1
      }
    }
```

#### Created the EKS cluster and worker nodes by using the EKS module
Used the `terraform-aws-modules/eks/aws` module. The cluster runs in the private subnets of the VPC above, with a managed node group `dev` of `t2.small` instances. Cluster creator admin permissions are enabled and the CoreDNS, kube-proxy and vpc-cni add-ons are added:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat eks-cluster.tf
    module "eks" {
      source  = "terraform-aws-modules/eks/aws"
      version = "21.25.0"
    
      name = "myapp-eks-cluster"
      kubernetes_version = "1.33"
    
      subnet_ids = module.myapp-vpc.private_subnets
      vpc_id = module.myapp-vpc.vpc_id
    
      endpoint_public_access = true
      enable_cluster_creator_admin_permissions = true
    ...
      eks_managed_node_groups = {
        dev = {
          ami_type       = "AL2023_x86_64_STANDARD"
          instance_types = ["t2.small"]
    
          min_size     = 1
          max_size     = 3
          desired_size = 3
        }
      }
    }
```

#### Applied configurations
After `terraform init`, the apply created 62 resources (VPC, subnets, NAT gateway, EKS cluster, node group, IAM roles and more). The cluster alone took about 8 minutes:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform apply --auto-approve
    ...
    module.eks.aws_eks_cluster.this[0]: Creation complete after 7m55s [id=myapp-eks-cluster]
    ...
    module.eks.module.eks_managed_node_group["dev"].aws_eks_node_group.this[0]: Creation complete after 1m48s [id=myapp-eks-cluster:dev-f0cb57967fd66cb58d0c4e27ff]
    ...
    Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
```
<img width="1706" height="831" alt="image" src="https://github.com/user-attachments/assets/dbcea9c7-e5ad-4f9e-b3a4-1af38ece890f" />
<img width="1708" height="515" alt="image" src="https://github.com/user-attachments/assets/3043e9b5-37f3-4fee-a4e7-7fd7dd185810" />
<img width="1700" height="371" alt="image" src="https://github.com/user-attachments/assets/0896ec69-bf4f-401c-adfe-fd96fe6aaf43" />
<img width="1708" height="727" alt="image" src="https://github.com/user-attachments/assets/bd721718-a254-4f6d-85fe-d2696a0a3a98" />
<img width="1708" height="819" alt="image" src="https://github.com/user-attachments/assets/083dfc5d-48fe-4cd8-b814-58958950c30e" />
<img width="1698" height="819" alt="image" src="https://github.com/user-attachments/assets/258e0495-3f51-4112-8f05-e3a2d68d84e8" />

#### Connected kubectl to the Cluster
Updated the local kubeconfig with the AWS CLI and checked that the three nodes are `Ready`:

```bash
    root@PC:~/modules/terraform (feature/eks)# aws eks update-kubeconfig --name myapp-eks-cluster --region eu-central-1
    Added new context arn:aws:eks:eu-central-1:731872836472:cluster/myapp-eks-cluster to /root/.kube/config
    
    root@PC:~/modules/terraform (feature/eks)# kubectl get node
    NAME                                          STATUS   ROLES    AGE   VERSION
    ip-10-0-1-175.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
    ip-10-0-2-147.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
    ip-10-0-3-48.eu-central-1.compute.internal    Ready    <none>   50m   v1.33.13-eks-cb19647
```

#### Deployed nginx Application/Pod
Deployed nginx with a Deployment (2 replicas) and a Service of type `LoadBalancer`, then got the load balancer's DNS name from `kubectl get svc`:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat nginx-config.yaml
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

    root@PC:~/modules/terraform (feature/eks)# kubectl apply -f./nginx-config.yaml
    deployment.apps/nginx created
    service/nginx configured

    root@PC:~/modules/terraform (feature/eks)# kubectl get pod
    NAME                     READY   STATUS    RESTARTS   AGE
    nginx-86c57bc6b8-mxkbd   1/1     Running   0          12s
    
    root@PC:~/modules/terraform (feature/eks)# kubectl get svc
    NAME         TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
    kubernetes   ClusterIP      172.20.0.1     <none>                                                                   443/TCP        71m
    nginx        LoadBalancer   172.20.3.243   a9e4950619e104317bd888cf6839b22f-825226598.eu-central-1.elb.amazonaws.com   80:31956/TCP   12m
```

<img width="1708" height="807" alt="image" src="https://github.com/user-attachments/assets/7641e6f9-83de-4142-a6e2-9431e78cd34c" />
<img width="1708" height="401" alt="image" src="https://github.com/user-attachments/assets/ecbc4483-dd23-4fb1-84d2-3a8967b43242" />

#### Terraform destroy
The first `terraform destroy` got stuck on the VPC. The load balancer and network interfaces created by Kubernetes are not in the Terraform state, so AWS refused to delete the VPC with `DependencyViolation`:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform destroy
    ...
    module.myapp-vpc.aws_vpc.this[0]: Still destroying... [id=vpc-0436e4eb7b3668acb, 12m52s elapsed]
    ^C
    Interrupt received.
    ...
    Error: deleting EC2 VPC (vpc-0436e4eb7b3668acb): operation error EC2: DeleteVpc, https response error StatusCode: 400, RequestID: 2105439e-1511-4369-bed0-736ad2d3ca2f, api error DependencyViolation: The vpc 'vpc-0436e4eb7b3668acb' has dependencies and cannot be deleted.
```

Deleted the leftover resources in the AWS console, then ran `terraform destroy` again. Nothing was left and the state is empty:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform destroy --auto-approve
    ...
    No changes. No objects need to be destroyed.
    Either you have not created any objects yet or the existing objects were already deleted outside of Terraform.
    Destroy complete! Resources: 0 destroyed.
    
    root@PC:~/modules/terraform (feature/eks)# terraform state list
    root@PC:~/modules/terraform (feature/eks)#
```
