# Java app with MySQL on EKS, deployed and migrated with Ansible

**Technologies:** Ansible (`kubernetes.core`, `community.docker`, `community.aws`), Terraform, AWS (EKS, VPC, ECR, EBS, Elastic Load Balancing), Kubernetes, Helm, ingress-nginx, Bitnami MySQL chart, Docker, Gradle, Java (Spring Boot), MySQL

A Java web app with a MySQL database on an EKS cluster, deployed entirely with Ansible so nobody has to run `kubectl` or write Helm commands by hand. Terraform creates the cluster. One playbook builds the app image and pushes it to ECR, another deploys the app with a single MySQL instance and an NGINX ingress so the app is reachable from the browser. A migration playbook then replaces the single MySQL with a replicated MySQL from a Helm chart (1 primary + 2 secondaries) while the app keeps running. A destroy playbook removes everything, including the AWS resources Kubernetes created on its own.

## How it works

```
terraform/                       VPC (3 public + 3 private subnets, NAT) + EKS (3 × t3.medium, EBS CSI driver)
        │
build-image-push-to-ecr.yaml     gradle build → ECR repo → docker login (ECR token) → build + push java-app:1.0
        │
deploy-to-cluster.yaml           kubeconfig ← terraform output
        │                        ingress-nginx chart → AWS load balancer
        │                        Secret + ConfigMap → MySQL Deployment (1 pod) → Java Deployment (3 pods) → Ingress
        │                        prints http://<load-balancer-dns>
        │
migrate-mysql-to-helm.yaml       MySQL chart: mysql-primary-0, mysql-secondary-0/1, one EBS volume each
        │                        ConfigMap DB_SERVER: db-server → mysql-primary
        │                        rollout restart of the Java pods, wait until ready
        │                        delete the old MySQL Deployment
        │
destroy.yaml                     ingress-nginx (load balancer) → MySQL chart → PVCs (EBS volumes)
                                 → terraform destroy → ECR repo
```

Inside the cluster:

```
browser ──> AWS load balancer ──> ingress-nginx ──> java-app-service ──> java-app (3 pods)
                                                                              │ DB_SERVER from ConfigMap
                                                       before migration:  db-server     → mysql (1 pod)
                                                       after migration:   mysql-primary → mysql-primary-0
                                                                                           ├ mysql-secondary-0
                                                                                           └ mysql-secondary-1
```

| File | What it does |
|---|---|
| `terraform/` | VPC and EKS cluster: managed add-ons, EBS CSI driver with Pod Identity and a default StorageClass, node group of 3 `t3.medium` nodes. |
| `java-app/` | The Spring Boot app and its `Dockerfile` (`eclipse-temurin:17-jre`). The app reads `DB_SERVER`, `DB_NAME`, `DB_USER` and `DB_PWD` from the environment. |
| `build-image-push-to-ecr.yaml` | Builds the jar, creates the ECR repository, logs in to ECR and builds and pushes the image. |
| `deploy-to-cluster.yaml` | Writes the kubeconfig, installs ingress-nginx, applies the Secret, ConfigMap, MySQL, Java app and Ingress, waits for the load balancer and prints its address. |
| `migrate-mysql-to-helm.yaml` | Installs the MySQL chart, points the ConfigMap to `mysql-primary`, restarts the Java pods and deletes the old MySQL. |
| `destroy.yaml` | Removes ingress-nginx, the MySQL chart and its PVCs, runs `terraform destroy` and deletes the ECR repository. |
| `k8s/db-secret.yaml`, `k8s/db-config.yaml` | DB credentials and connection settings. The Secret also holds the keys the MySQL chart expects (`mysql-root-password`, `mysql-password`, `mysql-replication-password`). |
| `k8s/mysql.yaml` | Single MySQL Deployment and its Service `db-server`. |
| `k8s/java-app.yaml` | Java Deployment (3 replicas, image from ECR) and Service `java-app-service`. |
| `k8s/java-app-ingress.yaml` | Routes `/` to `java-app-service` through the `nginx` ingress class. |
| `k8s/mysql-values.yaml`, `k8s/db-config-chart.yaml` | Values for the MySQL chart (replication, 2 secondaries, existing Secret) and the ConfigMap version that points to `mysql-primary`. |
| `test-all.sh`, `test.log` | End-to-end test run and its output. |

### Decisions

- **Image in ECR.** The EKS node role can already pull from ECR, so the pods need no `imagePullSecrets`. Pushing uses a 12-hour token from `aws ecr get-login-password` instead of a stored password.
- **Cluster name from Terraform.** The playbooks read it with `terraform output -raw cluster_name` and create the kubeconfig with `aws eks update-kubeconfig`, so nothing about the cluster is hardcoded.
- **Credentials in a Secret, settings in a ConfigMap.** Both pods read the same values. MySQL maps them to its own variable names (`MYSQL_USER` ← `DB_USER`), the Java app uses them under the names it expects.
- **Deploy order with waits.** MySQL is applied with `wait: true` before the Java app, so the app doesn't start against a database that isn't ready.
- **Ingress controller in its own namespace.** ingress-nginx runs in `ingress-nginx`, the Ingress resource stays next to the Service it routes to in `default`.
- **Migration without downtime.** The new MySQL is installed and ready first, then the ConfigMap is switched and the Java pods are restarted (pods only read environment variables at startup), and the old MySQL is deleted last. The app always has a database.
- **Writes go to the primary.** In the chart's replication mode only `mysql-primary` accepts writes, so `DB_SERVER` points to that Service.
- **Chart pinned to a version.** The MySQL chart is pinned to `14.0.3` and uses the `bitnamilegacy/mysql` image, since the regular Bitnami images are no longer published for free.
- **One tagged security group per node.** The node group also gets the cluster primary security group, and both carried the `kubernetes.io/cluster/<name>` tag. Kubernetes then refuses to create a load balancer. `node_security_group_tags` with `null` removes the tag from the node security group.
- **Destroy cleans up what Terraform doesn't know.** The load balancer of ingress-nginx and the EBS volumes of the MySQL PVCs are created by Kubernetes, not by Terraform. They are deleted first, with a pause for AWS to finish, so `terraform destroy` can remove the VPC and nothing is left that costs money.

## Requirements

- Terraform, AWS CLI, `kubectl`, `helm`, Docker, Gradle
- Ansible with the `kubernetes.core`, `community.docker` and `community.aws` collections, and `boto3`, `botocore` and `kubernetes` in the same Python environment
- AWS credentials with permissions for EC2, EKS, IAM, ECR and Elastic Load Balancing

## Usage

```bash
# 1. Cluster
terraform -chdir=terraform init
terraform -chdir=terraform apply -var-file=environments/dev.tfvars

# 2. Image
ansible-playbook build-image-push-to-ecr.yaml

# 3. App with a single MySQL (prints the app URL at the end)
ansible-playbook deploy-to-cluster.yaml

# 4. Replace MySQL with the replicated chart
ansible-playbook migrate-mysql-to-helm.yaml

# 5. Delete everything
ansible-playbook destroy.yaml
```

## Testing

`test-all.sh` runs steps 1–5 in order and stops at the first error. After the deploy and again after the migration it requests the app through the load balancer with `curl` until it gets `200`. After the migration it checks the MySQL pods, the `DB_SERVER` value inside a Java pod and that the old MySQL is gone. After the destroy it counts the EBS volumes and load balancers left in the account.

```bash
bash test-all.sh 2>&1 | tee test.log
```

Results from [`test.log`](./test.log):

- Deploy: 3 Java pods and 1 MySQL pod running with 0 restarts, the app answered `HTTP 200` through the load balancer.
- Migration: `mysql-primary-0`, `mysql-secondary-0` and `mysql-secondary-1` ready on three different nodes, each with an 8Gi EBS volume (`Bound`, `ebs-csi-default-sc`). The restarted Java pods had `DB_SERVER=mysql-primary`, the old `mysql-deployment` was gone, and the app still answered `HTTP 200`.
- All playbooks finished with `failed=0`.
- After the destroy: 0 EBS volumes from the cluster, 0 Classic load balancers, 0 ALB/NLB load balancers.
