# EKS environments with Terraform and two Jenkins pipelines

**Technologies:** Terraform, AWS (VPC, EKS, Fargate, EBS, IAM, S3, ECR), Helm, Helmfile, Kubernetes, Cluster Autoscaler, Jenkins, Docker, Gradle, Java, MySQL

One Terraform project creates the VPC, the EKS cluster with a node group and a Fargate profile, the EBS CSI driver, the Cluster Autoscaler and MySQL. The same code creates separate `dev`, `test` and `staging` environments. State is stored in S3. There are two Jenkins pipelines: one for the infrastructure (Terraform) and one for the application (build, push, deploy), the same split as a platform team and an app team working in separate repos.
Note: Only `dev` was applied. `test` and `staging` use the same pipeline with a different `ENV`.

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

| Namespace       | What                                        | Runs on        | Installed by                 |
| --------------- | ------------------------------------------- | -------------- | ---------------------------- |
| `default`     | MySQL (1 primary + 2 secondaries)           | EC2 node group | Terraform (`helm_release`) |
| `kube-system` | Cluster Autoscaler, EBS CSI driver, CoreDNS | EC2 node group | Terraform                    |
| `default`     | phpMyAdmin                                  | EC2 node group | app pipeline (Helmfile)      |
| `my-app`      | java-app (3 replicas)                       | Fargate        | app pipeline (Helmfile)      |

## Folder structure

```
02-projects/
├── terraform/                  → platform team (would be its own repo)
│   ├── Jenkinsfile
│   ├── providers.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── eks-cluster.tf
│   ├── autoscaler.tf
│   ├── mysql.tf
│   ├── outputs.tf
│   ├── environments/
│   │   ├── dev.tfvars
│   │   ├── test.tfvars
│   │   └── staging.tfvars
│   └── values/
│       └── mysql-values.yaml
└── app/                        → app team
    ├── Jenkinsfile
    ├── java-app/
    └── helm/
```

## Terraform project

### `providers.tf`

- **AWS provider** with `default_tags` (`environment`, `application`, `managed-by = terraform`). Every AWS resource Terraform creates gets these tags, so I didn't repeat `tags` in each module.
- **Helm provider** for MySQL and the Cluster Autoscaler. It connects to the new cluster with the outputs of the EKS module (endpoint, CA certificate) and gets a token with `aws eks get-token`, the same way a kubeconfig does. No kubeconfig file is needed.
- **S3 backend** : state is stored in the bucket `emre-myapp-tfstate-10`. `use_lockfile = true` puts a lock file next to the state during `apply`, so two runs can't change the state at the same time . The bucket was created once with the AWS CLI and versioning turned on.

### `variables.tf` and `environments/`

- `env_prefix` is the environment name. `local.cluster_name` is built from it (`dev-myapp-eks-cluster`), and the VPC, cluster and IAM role names all use it. IAM role names are global in the account, so without the prefix a second environment would fail with "role already exists".
- `environments/*.tfvars` hold the environment name and the CIDR ranges (`10.0.0.0/16` for dev, `10.1.0.0/16` for test, `10.2.0.0/16` for staging).
- `mysql_root_password` is a `sensitive` variable with no default. It comes from the environment variable `TF_VAR_mysql_root_password`, so the password is never in a file.
- Each environment has its own **Terraform workspace**, so each one has its own state file in S3 (`env:/dev/...`, `env:/test/...`).

### `vpc.tf`

3 private and 3 public subnets in 3 AZs, one NAT gateway (`single_nat_gateway`) to save cost, and the `kubernetes.io/...` subnet tags that EKS uses to find the subnets.

### `eks-cluster.tf`

- **Add-ons:** `coredns`, `kube-proxy`, `vpc-cni` and `eks-pod-identity-agent` as EKS managed add-ons; `vpc-cni` and `eks-pod-identity-agent` are installed before the nodes (`before_compute`) because nodes don't become `Ready` without a network plugin.
- **`aws-ebs-csi-driver` add-on:** creates the EBS volumes for the MySQL PVCs. It gets its IAM role through **Pod Identity**: `aws_ebs_csi_pod_identity` creates a role with the AWS EBS CSI policy, and `pod_identity_association` gives that role only to the driver's service account (`ebs-csi-controller-sa`), not to every pod on the node. `defaultStorageClass = { enabled = true }` creates a default StorageClass (`ebs-csi-default-sc`); new EKS versions don't have one, and the MySQL chart doesn't set a StorageClass, so its PVCs would stay `Pending` without it.
- **Node group `main`:** `t3.medium`, min 2, max 4, desired 3. `attach_cluster_primary_security_group = true` was added after the first deploy (see Problems below).
- **Fargate profile `fp-my-app`:** selects namespace `my-app`, where the app pipeline deploys java-app. It uses the cluster's private subnets and the module creates its pod execution role.
- **`enabled_log_types = []`:** turns off control plane logs to CloudWatch, which the module enables by default and costs money, not needed for the project.

### `autoscaler.tf`

- `cluster_autoscaler_pod_identity` creates an IAM role with the autoscaler policy, limited to this cluster, and binds it to the service account `cluster-autoscaler` in `kube-system`.
- `helm_release.cluster_autoscaler` installs the chart (`9.59.0`, autoscaler `1.35.0`) with `autoDiscovery.clusterName`, `awsRegion` and `rbac.serviceAccount.name = cluster-autoscaler`. The service account name must be the same as in the Pod Identity association, otherwise the autoscaler has no AWS permissions.
- Managed node groups get the autoscaler discovery tags from AWS, so nothing else is needed on the node group.

### `mysql.tf` and `values/mysql-values.yaml`

- `helm_release.mysql` installs the Bitnami MySQL chart `14.0.3` with `architecture: replication` and `secondary.replicaCount: 2`, so 3 MySQL pods in total, each with an 8Gi EBS volume.
- The image is `bitnamilegacy/mysql` with `allowInsecureImages: true`.
- The root password is passed with `set_sensitive` and `type = "string"`, so it is not shown in the plan.
- `depends_on = [module.eks]`. The exercise tip says `depends_on = [module.eks.cluster_name]`, but `depends_on` only accepts whole modules or resources, not attributes. Depending on the whole module also waits for the EBS CSI add-on, which MySQL needs for its volumes.

### `outputs.tf`

`cluster_name` and `cluster_endpoint`, printed at the end of each `apply`.

### `Jenkinsfile` (Terraform pipeline)

Pipeline job `terraform-eks`, Script Path `12-terraform/02-projects/terraform/Jenkinsfile`.

- **Parameters:** `ENV` (`dev` / `test` / `staging`) and `ACTION` (`apply` / `destroy`). The same Jenkinsfile manages every environment.
- **Credentials:** the AWS keys from Module 11 and a new Secret text `mysql-root-password`, given to Terraform as `TF_VAR_mysql_root_password`.
- **init:** `aws sts get-caller-identity` (shows which IAM user runs Terraform), `terraform init`, `terraform workspace select -or-create <ENV>`.
- **plan:** `terraform plan -var-file=environments/<ENV>.tfvars -out=tfplan`. With `ACTION=destroy` the plan gets `-destroy`, so deleting goes through the same plan and approval steps.
- **approve:** the pipeline waits until I read the plan and click **Yes**.
- **apply:** `terraform apply tfplan` applies exactly the plan that was approved.
- `-input=false` and `TF_IN_AUTOMATION=true`: Terraform fails instead of waiting for input that nobody can give in Jenkins, and leaves out hints meant for a human at a terminal.

**Jenkins setup.** Terraform `1.16.1` installed in the Jenkins container (same version as local, so the state is written by the same version). AWS CLI, Helm and Helmfile were already installed for Module 11.

## App side

- `helm/helmfile.yaml` deploys `phpmyadmin` and `java-app`. phpMyAdmin stays with the app team; it reads the root password from the `mysql` Secret that the MySQL chart creates.
- `Jenkinsfile`: all paths point to `12-terraform/02-projects/app/...` and `update-kubeconfig` uses the Terraform cluster name `dev-myapp-eks-cluster`.
- The ECR repo `java-app` created with `aws ecr create-repository`. It is shared by all environments, so it is not part of the per-environment Terraform project.

Pipeline job `java-app-tf`, Script Path `12-terraform/02-projects/app/Jenkinsfile`.

## Run

```bash
# once: state bucket
aws s3api create-bucket --bucket emre-myapp-tfstate-10 --region eu-central-1 \
  --create-bucket-configuration LocationConstraint=eu-central-1
aws s3api put-bucket-versioning --bucket emre-myapp-tfstate-10 \
  --versioning-configuration Status=Enabled
```

Then in Jenkins: `terraform-eks` with `ENV=dev`, `ACTION=apply`, approve the plan; after that `java-app-tf`.

Locally, for checks:

```bash
cd terraform
export TF_VAR_mysql_root_password='***'
terraform workspace select dev
terraform plan -var-file=environments/dev.tfvars
aws eks update-kubeconfig --name dev-myapp-eks-cluster --region eu-central-1
```

## Problems and fixes

**1. MySQL password rejected by the chart schema.** The first `apply` created everything except MySQL:

```
│ values don't meet the specifications of the schema(s) in the following
│ chart(s):
│ mysql:
│ - at '/auth/rootPassword': got number, want string
```

Helm guesses the type of `set` values, and a password made only of digits became a number. Adding `type = "string"` to `set_sensitive` fixed it; the next run only created `helm_release.mysql` (`Plan: 1 to add, 0 to change, 0 to destroy.`).

**2. java-app on Fargate couldn't reach DNS or MySQL.** The java-app pods kept restarting:

```
Caused by: com.mysql.cj.exceptions.CJCommunicationsException: Communications link failure
...
Caused by: java.net.UnknownHostException: mysql-primary.default: Name or service not known
```

Fargate pods use the EKS cluster primary security group. The EC2 nodes (where CoreDNS and MySQL run) only had the node security group of the Terraform module, which allows a fixed list of ports and doesn't accept traffic from the primary security group. Adding `attach_cluster_primary_security_group = true` to the node group fixed it. Terraform updated the launch template and the node group (`Plan: 0 to add, 2 to change, 0 to destroy.`), and EKS replaced the nodes one by one. After a `kubectl rollout restart` the java-app pods ran with 0 restarts.

**3. A MySQL pod stayed `Pending` after the nodes were replaced.** After the node replacement the node group had 2 nodes, in eu-central-1a and eu-central-1c. `mysql-secondary-0` had its EBS volume in eu-central-1b, and an EBS volume can only be attached in its own AZ:

```
  Warning  FailedScheduling   4m38s (x12 over 6m21s)  default-scheduler   0/6 nodes are available: 2 node(s) didn't match PersistentVolume's node affinity, 4 node(s) had untolerated taint(s). no new claims to deallocate, preemption: 0/6 nodes are available: 6 Preemption is not helpful for scheduling.
  Normal   NotTriggerScaleUp  3m14s (x31 over 8m15s)  cluster-autoscaler  pod didn't trigger scale-up: 1 node(s) didn't match PersistentVolume's node affinity
```

The Cluster Autoscaler didn't add a node, because the one node group spans 3 AZs and it can't choose the AZ of a new node. I set the node group back to 3 nodes with `aws eks update-nodegroup-config ... desiredSize=3`; AWS put the new node in eu-central-1b and the pod started. Terraform ignores `desired_size` after creation, so this doesn't cause drift. The better long-term fix is one node group per AZ with the autoscaler option `balance-similar-node-groups`.

## Result

The Terraform pipeline runs as the IAM user that also owns the cluster admin access entry:

```
+ aws sts get-caller-identity
...
    "Arn": "arn:aws:iam::731872836472:user/admin"
...
+ terraform workspace select -or-create dev
```

Second run after the MySQL fix:

```
Plan: 1 to add, 0 to change, 0 to destroy.
...
Run apply on dev?
Yes or Abort
Approved by emre
...
helm_release.mysql: Creation complete after 1m45s [id=mysql]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

cluster_endpoint = "https://4****325AD3F5BE70F8840F7F96A575DA.gr7.eu-central-1.eks.amazonaws.com"
cluster_name = "dev-myapp-eks-cluster"
...
Finished: SUCCESS
```

Security group fix:

```
      ~ vpc_security_group_ids               = [
          + "sg-0d7558c6e622ddae9",
            # (1 unchanged element hidden)
        ]
...
Plan: 0 to add, 2 to change, 0 to destroy.
...
module.eks.module.eks_managed_node_group["main"].aws_eks_node_group.this[0]: Modifications complete after 15m32s [id=dev-myapp-eks-cluster:main-2157685631b6ba583ab038592d]

Apply complete! Resources: 0 added, 2 changed, 0 destroyed.
...
Finished: SUCCESS
```

State in S3, in the `dev` workspace path:

```
root@PC:~/twn/devops-bootcamp-update (main)# aws s3 ls s3://emre-myapp-tfstate-10 --recursive
2026-10-15 17:34:08     286372 env:/dev/myapp/terraform.tfstate
```

The app pipeline built version `1.2.0`, pushed it to ECR, deployed it with Helmfile and committed the new version:

```
+ gradle clean build
...
BUILD SUCCESSFUL in 20s
...
+ docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-app:1.2.0-1
...
1.2.0-1: digest: sha256:cf520b27ee41f2c23cc8f018230e4b30c505a571c06282f412cead74c10226c9 size: 856
...
+ aws eks update-kubeconfig --name dev-myapp-eks-cluster --region eu-central-1
...
+ helmfile sync --set appVersion=1.2.0-1
...
NAME         NAMESPACE   CHART                 VERSION   DURATION
phpmyadmin   default     ./charts/phpmyadmin   0.1.0           3s
java-app     my-app      ./charts/java-app     0.1.0           4s
...
+ git push origin HEAD:main
To https://github.com/emrearabacioglu/devops-bootcamp.git
   842ec12..546f221  HEAD -> main
...
Finished: SUCCESS
```

Helm releases installed by Terraform, and the default StorageClass from the EBS CSI add-on:

```
NAME                    NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                           APP VERSION
cluster-autoscaler      kube-system     1               2026-10-15 13:52:54.748172927 +0000 UTC deployed        cluster-autoscaler-9.59.0       1.35.0
mysql                   default         1               2026-10-15 13:59:50.408128074 +0000 UTC deployed        mysql-14.0.3                    9.4.0
```

```
NAME                           PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
ebs-csi-default-sc (default)   ebs.csi.aws.com         Delete          WaitForFirstConsumer   true                   13m
gp2                            kubernetes.io/aws-ebs   Delete          WaitForFirstConsumer   false                  21m
```

Three MySQL volumes:

```
NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS         VOLUMEATTRIBUTESCLASS   AGE
data-mysql-primary-0     Bound    pvc-a6a78d98-5c63-4cbb-9419-59bf80d23321   8Gi        RWO            ebs-csi-default-sc   <unset>                 5m20s
data-mysql-secondary-0   Bound    pvc-19f0771a-7351-4039-9477-d79443e9db68   8Gi        RWO            ebs-csi-default-sc   <unset>                 5m20s
data-mysql-secondary-1   Bound    pvc-69c15c39-1636-441b-a6d1-72aecd420d68   8Gi        RWO            ebs-csi-default-sc   <unset>                 4m16s
```

The Cluster Autoscaler runs with its IAM role and checks the node group:

```
I1015 14:05:30.658805       1 klogx.go:87] Node ip-10-0-3-169.eu-central-1.compute.internal - cpu requested is 9.32642% of allocatable
I1015 14:05:30.659024       1 eligibility.go:163] Node ip-10-0-1-208.eu-central-1.compute.internal unremovable: cpu requested (69.4301% of allocatable) is above the scale-down utilization threshold
...
I1015 14:05:30.659172       1 cluster.go:160] Node ip-10-0-3-169.eu-central-1.compute.internal may be removed
```

Final state: 3 EC2 nodes in 3 AZs plus the Fargate nodes for java-app:

```
NAME                                                  STATUS   ROLES    AGE     VERSION               ZONE
fargate-ip-10-0-1-83.eu-central-1.compute.internal    Ready    <none>   11m     v1.35.8-eks-1ccbad1   eu-central-1a
fargate-ip-10-0-2-182.eu-central-1.compute.internal   Ready    <none>   9m54s   v1.35.8-eks-1ccbad1   eu-central-1b
fargate-ip-10-0-2-197.eu-central-1.compute.internal   Ready    <none>   10m     v1.35.8-eks-1ccbad1   eu-central-1b
ip-10-0-1-90.eu-central-1.compute.internal            Ready    <none>   26m     v1.35.8-eks-b9510e3   eu-central-1a
ip-10-0-2-60.eu-central-1.compute.internal            Ready    <none>   2m17s   v1.35.8-eks-b9510e3   eu-central-1b
ip-10-0-3-113.eu-central-1.compute.internal           Ready    <none>   28m     v1.35.8-eks-b9510e3   eu-central-1c
```

MySQL and phpMyAdmin on EC2 nodes:

```
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE                                          NOMINATED NODE   READINESS GATES
mysql-primary-0               1/1     Running   0          24m   10.0.1.17    ip-10-0-1-90.eu-central-1.compute.internal    <none>           <none>
mysql-secondary-0             1/1     Running   0          14m   10.0.2.128   ip-10-0-2-60.eu-central-1.compute.internal    <none>           <none>
mysql-secondary-1             1/1     Running   0          24m   10.0.1.121   ip-10-0-1-90.eu-central-1.compute.internal    <none>           <none>
phpmyadmin-67cbcfc865-k8cqr   1/1     Running   0          21m   10.0.3.224   ip-10-0-3-113.eu-central-1.compute.internal   <none>           <none>
```

java-app on Fargate, running with 0 restarts after the security group fix:

```
my-app        java-app-deployment-6c4c686b57-8mv5s                         1/1     Running   0          5m24s   10.0.2.182   fargate-ip-10-0-2-182.eu-central-1.compute.internal   <none>           <none>
my-app        java-app-deployment-6c4c686b57-jf4xs                         1/1     Running   0          7m9s    10.0.1.83    fargate-ip-10-0-1-83.eu-central-1.compute.internal    <none>           <none>
my-app        java-app-deployment-6c4c686b57-lm9kq                         1/1     Running   0          6m18s   10.0.2.197   fargate-ip-10-0-2-197.eu-central-1.compute.internal   <none>           <none>
```

I opened the app and phpMyAdmin through `kubectl port-forward` (`localhost:8080`, `localhost:8081`); both worked.
