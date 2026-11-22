# EKS environments with Terraform: Jenkins pipelines, and GitHub Actions with Argo CD

**Technologies:** Terraform, AWS (VPC, EKS, Fargate, EBS, IAM, S3, ECR, Secrets Manager), Helm, Helmfile, Kubernetes, Cluster Autoscaler, Jenkins, GitHub Actions, OIDC, Argo CD, External Secrets Operator, Claude, Docker, Gradle, Java, MySQL

One Terraform project creates the VPC, the EKS cluster with a node group and a Fargate profile, the EBS CSI driver, the Cluster Autoscaler and MySQL. The same code creates separate `dev`, `test` and `staging` environments, each with its own state in S3. Two Jenkins pipelines split the work the way a platform team and an app team would: one manages the infrastructure with Terraform, the other builds the Java app and deploys it into the cluster.

The project has a second version of the same delivery, next to the Jenkins one: [GitHub Actions with OIDC, Argo CD and a Claude plan review](#github-actions-and-argo-cd-version).

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

## GitHub Actions and Argo CD version

The same environments, delivered without Jenkins and without stored AWS keys. GitHub Actions gets short-lived AWS credentials through OIDC. The infrastructure workflow keeps the plan, approve, apply flow. The app workflow doesn't deploy anymore: it writes the new image tag to Git, and Argo CD in the cluster syncs it. On pull requests, Claude reads the Terraform plan and comments a risk summary.

The Jenkins files are unchanged. Everything new in the Terraform project is behind `gitops_enabled`, which only the GitHub Actions workflow sets, so a Jenkins run still creates exactly the environment described above.

### How it works

```
bootstrap/ (once per account)   GitHub OIDC provider + 3 IAM roles
                                  gha-terraform-plan   read-only     sub = pull_request | ref:main
                                  gha-terraform-apply  admin         sub = environment:dev|test|staging
                                  gha-ecr-push         push java-app sub = ref:main

pull request ──> terraform-eks.yml
                   plan (plan role) ──> plan.txt ──> Claude ──> risk summary comment on the PR

manual run ────> terraform-eks.yml
                   plan (plan role) ──> tfplan artifact ──> approval in GitHub Environment ──> apply tfplan (apply role)
                                                                                                   │
                     Secrets Manager <env>/myapp/db, External Secrets, Argo CD + root app <────────┘

app change ────> java-app-gitops.yml
                   version bump ──> gradle build ──> push to ECR (ecr-push role)
                   ──> appVersion in app/gitops/envs/<env>/values/java-app.yaml ──> commit to main
                                                                                       │
Argo CD (in the cluster) <── watches app/gitops/envs/<env>/ on main ───────────────────┘
  ├ secrets     ClusterSecretStore + ExternalSecret ──> Secret db-secret in my-app
  ├ java-app    chart app/helm/charts/java-app + env values ──> my-app (Fargate)
  └ phpmyadmin  chart app/helm/charts/phpmyadmin ──> default
```

| File | What it does |
|---|---|
| `bootstrap/` | Separate Terraform project, applied once by hand. GitHub OIDC provider and the three roles. State in the same bucket under `bootstrap/`. |
| `.github/workflows/terraform-eks.yml` | Infrastructure workflow. PR: fmt, validate, plan for `dev`, Claude review. Manual run with `env` and `action`: plan, approval, apply of the saved plan. |
| `.github/workflows/java-app-gitops.yml` | App workflow. Version bump, build, image to ECR, new tag in the environment's values file, commit to `main`. |
| `terraform/gitops.tf` | Secrets Manager secret with the DB credentials, External Secrets Operator with a Pod Identity role, Argo CD, and the root Application for the environment. |
| `terraform/variables.tf` | `gitops_enabled`, the Argo CD repository and branch, the plan role name and `cluster_admin_arns` for your own `kubectl` access. |
| `app/gitops/envs/<env>/` | What Argo CD deploys into one environment: the `secrets`, `java-app` and `phpmyadmin` Applications, the values file and the External Secrets manifests. |
| `app/helm/charts/java-app` | New `existingSecret` value. When set, the chart creates no Secret and loads the keys of an existing one with `envFrom`. Empty by default, so the Helmfile output is the same as before. |

### Decisions

- **No AWS keys in GitHub.** Each job gets a GitHub OIDC token, and AWS exchanges it for temporary credentials of one role. The trust policies check the `sub` claim, so a token from another repository or another branch is refused.
- **Plan and apply are different roles.** Plans run with a read-only role. Only the apply job has the admin role, and its trust policy accepts only tokens that carry `environment:<env>`. A job gets that claim only by running in the GitHub Environment, and the environment has required reviewers. The approval and the permission are the same gate: nobody can skip the approval and still get the role.
- **The approved plan is the applied plan.** The plan job uploads the binary `tfplan`, the apply job downloads it and runs `terraform apply tfplan`. The provider lock file is committed, so both jobs use the same provider versions. The binary plan can contain the MySQL password, so the artifact is kept for 1 day.
- **The plan role can read the cluster, not change it.** Refreshing the Helm releases needs the cluster, so the plan role gets an EKS access entry with `AmazonEKSAdminViewPolicy` (the View policy can't read Secrets, where Helm keeps its releases). The apply role is the cluster creator and gets admin.
- **CI has no access to the cluster.** The app workflow only pushes an image and a commit. Argo CD pulls the change. What runs in the cluster is always what is in Git, and `selfHeal` reverts manual changes.
- **App of apps per environment.** Terraform installs Argo CD and one root Application that points to `app/gitops/envs/<env>/`. Adding an app to an environment means adding a manifest there, not changing Terraform.
- **Charts reused, values per environment.** The Argo CD Applications use the existing charts in `app/helm/charts` with a second source (`ref: values`) for the environment's values file. Promoting a version to `test` or `staging` is a change to that environment's `appVersion`.
- **No passwords in Git.** The Helmfile values have the DB password in the file. In this version Terraform writes the credentials to Secrets Manager (`<env>/myapp/db`), and External Secrets copies them into the `db-secret` Secret. The operator's Pod Identity role can read only this one secret. `recovery_window_in_days = 0` deletes the secret at once on destroy, so the environment can be created again with the same name.
- **Claude can't write to GitHub.** The review job gives Claude only `Read` and `Write` and tells it to treat the plan as data. It writes `risk-summary.md`, and a normal step posts that file with `gh pr comment --edit-last`, so every push updates one comment instead of adding a new one. The job doesn't run for fork PRs.
- **A bot commit can't start a loop.** A push made with `GITHUB_TOKEN` doesn't start new workflow runs.
- **Known limitation: Argo CD follows `main`.** Manual runs (`workflow_dispatch`) only show up for workflows on the default branch, and Argo CD reads `main`, so this version is tested after the PR is merged.

### Requirements

- Everything from the Jenkins version except Jenkins: the state bucket and the `java-app` ECR repository.
- Terraform `1.16.1` locally, once, for `bootstrap/`.
- GitHub repository settings:
  - Environments `dev`, `test`, `staging`, each with a required reviewer
  - Secrets `MYSQL_ROOT_PASSWORD` and `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`, uses a Claude subscription instead of API billing)
  - Variables `AWS_PLAN_ROLE_ARN`, `AWS_APPLY_ROLE_ARN`, `AWS_ECR_PUSH_ROLE_ARN` (from the `bootstrap` outputs), and `CLUSTER_ADMIN_ARNS`, a JSON list with your IAM user ARN, e.g. `["arn:aws:iam::<account>:user/<name>"]`

### Usage

Once, the OIDC provider and the roles:

```bash
cd bootstrap
terraform init
terraform apply
terraform output
```

If the account already has an OIDC provider for `token.actions.githubusercontent.com`, import it first with `terraform import aws_iam_openid_connect_provider.github <its ARN>`.

Then:

1. Open a PR that changes `terraform/`. The `terraform-eks` workflow plans `dev` and Claude comments the risk summary.
2. After the merge, run `terraform-eks` with `env=dev` and `action=apply`, and approve the `dev` deployment when the plan looks right.
3. Run `java-app-gitops` with `env=dev`. It pushes a new image and commits the tag, and Argo CD deploys it.
4. Check it:

```bash
aws eks update-kubeconfig --name dev-myapp-eks-cluster --region eu-central-1
kubectl get applications -n argocd
kubectl get externalsecret,secret db-secret -n my-app
kubectl get pods -n my-app
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

5. Delete it: run `terraform-eks` with `env=dev` and `action=destroy` and approve.

### Result

_To be filled in after the `dev` test run._
