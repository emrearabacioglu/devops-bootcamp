# Java app with MySQL on EKS, deployed by a Jenkins pipeline

**Technologies:** AWS EKS, AWS Fargate, Amazon ECR, eksctl, Kubernetes, Helm, Helmfile, Jenkins, Docker, Gradle, Java, MySQL

A Java (Spring Boot) app with a MySQL database and phpMyAdmin on an EKS cluster. MySQL and phpMyAdmin run on EC2 worker nodes, the Java app runs on Fargate. A Jenkins pipeline increases the app version, builds the jar and the Docker image, pushes the image to ECR, deploys everything with Helmfile and commits the new version back to Git.

## How it works

```
GitHub ──checkout──> Jenkins ──push image──> ECR
                        │                     │
                  helmfile sync          image pull
                        │                     │
                        └──> EKS cluster <────┘
```

Jenkins only gives the image address and tag to Kubernetes. The cluster pulls the image from ECR itself.

| Namespace | Release | Runs on | Why |
|---|---|---|---|
| `default` | `mysql` (primary + secondary), `phpmyadmin` | EC2 node group | MySQL needs EBS volumes, Fargate can't mount EBS |
| `my-app` | `java-app` (3 replicas) | Fargate | The Fargate profile selects namespace `my-app` |

Pipeline stages:

```
increment version → build app → build image → deploy → commit version update
1.0.0 → 1.1.0       gradle       docker build   helmfile sync    git push build.gradle
tag 1.1.0-<build>                + push to ECR  --set appVersion
```

| File | What it does |
|---|---|
| `eks/cluster.yaml` | eksctl config: managed node group (`t3.medium`, 1–3 nodes), Fargate profile for namespace `my-app`, OIDC provider and the EBS CSI driver add-on with a default StorageClass. |
| `java-app/` | The Spring Boot app and its `Dockerfile`. The app reads `DB_USER`, `DB_PWD`, `DB_SERVER` and `DB_NAME` from the environment. |
| `helm/helmfile.yaml` | Three releases: `mysql` from the Bitnami repo, `phpmyadmin` and `java-app` from the local charts. |
| `helm/values/mysql-values.yaml` | MySQL in replication mode (primary + 1 secondary), root password, database `my-app-db`. |
| `helm/values/java-app-values.yaml` | 3 replicas, the ECR image, `DB_SERVER: mysql-primary.default` and the DB credentials. |
| `helm/charts/java-app` | Deployment, Service (ClusterIP, 8080), ConfigMap `db-config` and Secret `db-secret`. |
| `helm/charts/phpmyadmin` | Deployment and Service `phpmyadmin-service` (8081 → 80), connected to `mysql-primary`. |
| `Jenkinsfile` | The pipeline above. |

### Decisions

- **Cluster as a config file.** `eksctl create cluster -f cluster.yaml` instead of CLI flags, so the setup is in Git and can be recreated with one command.
- **Fargate only for the app.** The Fargate profile selects only `my-app`. If `default` were included, MySQL would also be scheduled on Fargate, where its EBS volumes can't be mounted.
- **EBS permissions only for the CSI driver.** `withOIDC: true` lets the EBS CSI driver get its own IAM role (IRSA), so only the driver can create volumes, not every pod on the node.
- **Default StorageClass from the add-on.** New EKS versions have no default StorageClass and the MySQL chart doesn't set one. Without `defaultStorageClass.enabled: true` the MySQL PVCs would stay `Pending`.
- **Helmfile for all releases.** One `helmfile sync` installs or updates all three releases, and the pipeline only passes the image tag.
- **Cross-namespace DB address.** The app runs in `my-app` and MySQL in `default`, so `DB_SERVER` is `mysql-primary.default`.
- **No `imagePullSecrets`.** On EKS the node role and the Fargate pod execution role already have read access to ECR.
- **One place for the root password.** phpMyAdmin reads it from the Secret that the MySQL chart creates.
- **Unique image tags.** The tag is `<version>-<BUILD_NUMBER>`. If a build fails after pushing an image, the next build gets a different tag and nothing is overwritten.
- **One jar in `build/libs`.** `jar { enabled = false }` turns off the extra `-plain.jar`, so `COPY build/libs/*.jar` in the Dockerfile matches one file whatever the version is.
- **Java 17 output from a Java 21 build.** The Jenkins container has Java 21 only, so `build.gradle` uses `options.release = 17` instead of a Java 17 toolchain.
- **Short-lived credentials.** The pipeline gets a fresh ECR token and creates the kubeconfig with `aws eks update-kubeconfig` on every build. Nothing is copied to Jenkins by hand.
- **Version commit without a build loop.** Only `build.gradle` is committed, to the same branch the job builds, so the next build reads the new version. The job is started manually, so the commit doesn't trigger another build.

## Requirements

- AWS CLI, `eksctl`, `kubectl`
- Jenkins with Docker, AWS CLI, Helm and Helmfile available to the pipeline, a Gradle tool named `gradle-8`
- Jenkins credentials: `jenkins_aws_access_key_id`, `jenkins_aws_access_secret_key` (AWS keys) and `github-credentials` (to push the version commit)
- A Pipeline job using "Pipeline script from SCM", branch `*/main`, Script Path `11-eks/02-projects/Jenkinsfile`

## Usage

```bash
aws ecr create-repository --repository-name java-app --region eu-central-1
cd eks
eksctl create cluster -f cluster.yaml
```

Then **Build Now** on the Jenkins job. To open the app and phpMyAdmin:

```bash
kubectl port-forward svc/java-app-service 8080:8080 -n my-app
kubectl port-forward svc/phpmyadmin-service 8081:8081
```

## Result

- The cluster came up with the managed node group, the Fargate profile `fp-my-app` and the EBS CSI add-on. `ebs-csi-default-sc` was the default StorageClass.
- The pipeline built version `1.1.0`, pushed `java-app:1.1.0-2` to ECR, installed the three releases with Helmfile and pushed the version commit to `main`.
- MySQL (`mysql-primary-0`, `mysql-secondary-0`) and phpMyAdmin ran on the EC2 nodes, the three java-app pods on their own Fargate nodes.
- Both MySQL PVCs were `Bound` to 8Gi EBS volumes from the default StorageClass.
- The app (`localhost:8080`) and phpMyAdmin (`localhost:8081`) opened through port-forward, and phpMyAdmin showed the `my-app-db` database.

<img width="1240" height="421" alt="image" src="https://github.com/user-attachments/assets/08f9aebf-149d-4399-b16b-20e127844c6c" />
