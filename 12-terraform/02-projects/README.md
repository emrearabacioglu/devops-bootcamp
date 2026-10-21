# EKS environments with Terraform and two Jenkins pipelines

**Technologies:** Terraform, AWS (VPC, EKS, Fargate, EBS, IAM, S3, ECR), Helm, Helmfile, Kubernetes, Cluster Autoscaler, Jenkins, Docker, Gradle, Java, MySQL

One Terraform project creates the VPC, the EKS cluster with a node group and a Fargate profile, the EBS CSI driver, the Cluster Autoscaler and MySQL. The same code creates separate `dev`, `test` and `staging` environments, each with its own state in S3. Two Jenkins pipelines split the work the way a platform team and an app team would: one manages the infrastructure with Terraform, the other builds the Java app and deploys it into the cluster.

## How it works

```
                 platform team                               app team
          ┌──────────────────────────┐            ┌──────────────────────────────┐
GitHub ──>│ terraform-eks pipeline   │            │ java-app-tf pipeline         │<── GitHub
          │ init → plan → approve →  │            │ version bump → gradle build →│
          │ apply                    │            │ docker push → helmfile sync →│
          └────────────┬─────────────┘            │ commit version               │
                       │                          └───────┬──────────────┬───────┘
          state in S3 <┤                                  │              │
                       ▼                                  ▼              ▼
          VPC, EKS, node group, Fargate profile,        ECR      java-app + phpMyAdmin
          EBS CSI, Cluster Autoscaler, MySQL ──────────────────> on the same cluster
```

Terraform builds the environment, including the database. The app pipeline only deploys the application into it.

| Namespace | What | Runs on | Installed by |
|---|---|---|---|
| `default` | MySQL (1 primary + 2 secondaries) | EC2 node group | Terraform (`helm_release`) |
| `kube-system` | Cluster Autoscaler, EBS CSI driver, CoreDNS | EC2 node group | Terraform |
| `default` | phpMyAdmin | EC2 node group | app pipeline (Helmfile) |
| `my-app` | java-app (3 replicas) | Fargate | app pipeline (Helmfile) |

| File | What it does |
|---|---|
| `terraform/providers.tf` | AWS provider with default tags, Helm provider connected to the new cluster, S3 backend with a lock file. |
| `terraform/variables.tf`, `terraform/environments/*.tfvars` | Environment name and CIDR ranges per environment. The cluster, VPC and IAM names are built from the environment name. |
| `terraform/vpc.tf` | 3 private and 3 public subnets in 3 AZs, one NAT gateway, the subnet tags EKS needs. |
| `terraform/eks-cluster.tf` | EKS cluster, managed add-ons, EBS CSI driver with Pod Identity, node group `main` (`t3.medium`, 2–4 nodes), Fargate profile for `my-app`. |
| `terraform/autoscaler.tf` | IAM role for the Cluster Autoscaler through Pod Identity and the autoscaler Helm chart. |
| `terraform/mysql.tf`, `terraform/values/mysql-values.yaml` | Bitnami MySQL chart in replication mode with 2 secondaries, each pod with an 8Gi EBS volume. |
| `terraform/Jenkinsfile` | Infrastructure pipeline with `ENV` and `ACTION` parameters. |
| `app/Jenkinsfile`, `app/helm/`, `app/java-app/` | App pipeline: version bump, build, push to ECR, Helmfile deploy of `java-app` and `phpmyadmin`. |

### Decisions

- **One codebase, many environments.** Each environment is a Terraform workspace with its own state file in S3 (`env:/dev/...`). Resource names include the environment name, because IAM role names are global in the account and a second environment would otherwise clash.
- **Shared state with locking.** State lives in a versioned S3 bucket, and `use_lockfile = true` stops two runs from changing it at the same time.
- **No secrets in files.** The MySQL root password is a `sensitive` variable with no default, passed as `TF_VAR_mysql_root_password` from a Jenkins credential and set with `set_sensitive` so it doesn't show in the plan. `type = "string"` keeps a password of only digits from being sent to the chart as a number.
- **Helm provider without a kubeconfig.** It connects with the EKS module outputs and gets a token with `aws eks get-token`.
- **Least privilege through Pod Identity.** The EBS CSI driver and the Cluster Autoscaler each get their own IAM role, bound to their service account only, not to every pod on the node.
- **Default StorageClass from the add-on.** New EKS versions have no default StorageClass and the MySQL chart doesn't set one, so its PVCs would stay `Pending` without it.
- **Network plugin before the nodes.** `vpc-cni` and `eks-pod-identity-agent` are installed with `before_compute`, because nodes don't become `Ready` without a network plugin.
- **Cluster primary security group on the nodes.** Fargate pods use the cluster primary security group, which the default node security group doesn't accept. Attaching it to the node group lets the java-app pods on Fargate reach CoreDNS and MySQL on the EC2 nodes.
- **MySQL waits for the whole EKS module.** `depends_on = [module.eks]` also waits for the EBS CSI add-on, which MySQL needs for its volumes.
- **Plan, approve, apply.** The pipeline applies exactly the plan that was approved. `ACTION=destroy` goes through the same plan and approval steps. `-input=false` and `TF_IN_AUTOMATION=true` make Terraform fail instead of waiting for input in Jenkins.
- **Shared ECR repository.** The `java-app` repository is used by all environments, so it is created once outside the per-environment Terraform project.
- **Control plane logs off.** `enabled_log_types = []` turns off CloudWatch logging, which the module enables by default and which costs money.
- **Known limitation: one node group across 3 AZs.** An EBS volume can only be attached in its own AZ. If no node is left in that AZ, the MySQL pod stays `Pending`, and the Cluster Autoscaler can't help because it can't choose the AZ of a new node in a multi-AZ group. One node group per AZ with `balance-similar-node-groups` would fix this.

## Requirements

- Terraform, AWS CLI, `kubectl`
- An S3 bucket for the state (`emre-myapp-tfstate-10`) with versioning on
- Jenkins with Terraform, Docker, AWS CLI, Helm and Helmfile, a Gradle tool named `gradle-8`
- Jenkins credentials: `jenkins_aws_access_key_id`, `jenkins_aws_access_secret_key`, `mysql-root-password` (Secret text) and `github-credentials`
- Pipeline jobs `terraform-eks` (Script Path `12-terraform/02-projects/terraform/Jenkinsfile`) and `java-app-tf` (Script Path `12-terraform/02-projects/app/Jenkinsfile`)

## Usage

Once, the state bucket and the ECR repository:

```bash
aws s3api create-bucket --bucket emre-myapp-tfstate-10 --region eu-central-1 \
  --create-bucket-configuration LocationConstraint=eu-central-1
aws s3api put-bucket-versioning --bucket emre-myapp-tfstate-10 \
  --versioning-configuration Status=Enabled
aws ecr create-repository --repository-name java-app --region eu-central-1
```

Then in Jenkins: run `terraform-eks` with `ENV=dev` and `ACTION=apply`, approve the plan, then run `java-app-tf`. To delete the environment, run `terraform-eks` with `ACTION=destroy`.

Locally, for checks:

```bash
cd terraform
export TF_VAR_mysql_root_password='***'
terraform workspace select dev
terraform plan -var-file=environments/dev.tfvars
aws eks update-kubeconfig --name dev-myapp-eks-cluster --region eu-central-1
```

## Result

Only `dev` was applied. `test` and `staging` use the same pipeline with a different `ENV`.

- The Terraform pipeline planned, waited for approval and applied. State was written to `env:/dev/myapp/terraform.tfstate` in the S3 bucket.
- Terraform installed the Cluster Autoscaler (`9.59.0`) and MySQL (`14.0.3`). The three MySQL PVCs were `Bound` to 8Gi EBS volumes from `ebs-csi-default-sc`.
- The Cluster Autoscaler ran with its IAM role and evaluated the nodes for scale-down.
- The app pipeline built version `1.2.0`, pushed `java-app:1.2.0-1` to ECR, deployed `java-app` and `phpmyadmin` with Helmfile and pushed the version commit.
- Final state: 3 EC2 nodes in 3 AZs running MySQL and phpMyAdmin, and the three java-app pods on Fargate with 0 restarts.
- The app and phpMyAdmin opened through `kubectl port-forward` (`localhost:8080`, `localhost:8081`).
