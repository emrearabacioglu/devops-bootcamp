# Module 11 – EKS exercise: Java app with MySQL on EKS, deployed by Jenkins

**Technologies:** AWS EKS, AWS Fargate, Amazon ECR, eksctl, Kubernetes, Helm, Helmfile, Jenkins, Docker, Gradle, Java, MySQL

A Java (Spring Boot) app with a MySQL database and phpMyAdmin on an EKS cluster. MySQL and phpMyAdmin run on EC2 worker nodes, the Java app runs on Fargate. A Jenkins pipeline increases the app version, builds the jar and the Docker image, pushes the image to ECR, deploys everything with Helmfile and commits the new version back to Git.

## How pipeline works

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

The Java app connects to `mysql-primary.default:3306`. phpMyAdmin connects to `mysql-primary`.

## Folder structure

```
02-projects/
├── Jenkinsfile
├── eks/
│   └── cluster.yaml
├── java-app/
│   ├── Dockerfile
│   ├── build.gradle
│   ├── settings.gradle
│   └── src/
└── helm/
    ├── helmfile.yaml
    ├── values/
    │   ├── mysql-values.yaml
    │   └── java-app-values.yaml
    └── charts/
        ├── java-app/
        └── phpmyadmin/
```

## File descriptions

### `eks/cluster.yaml`

An eksctl config file instead of CLI flags, so the cluster setup is in Git and can be created again with one command. I checked it with `eksctl create cluster -f cluster.yaml --dry-run` before creating the cluster.

- **`managedNodeGroups` (`demo-nodes`):** `t3.medium`, desired 2, min 1, max 3. `withAddonPolicies.autoScaler: true` adds the IAM permissions for Cluster Autoscaler to the node role.
- **`fargateProfiles` (`fp-my-app`):** only namespace `my-app`. `default` is left out on purpose, otherwise MySQL would also be scheduled on Fargate and its volumes wouldn't work.
- **`iam.withOIDC: true`:** lets a single pod get its own IAM role (IRSA). The EBS CSI driver uses it, so only the driver can create EBS volumes, not every pod on the node.
- **`addons` (`aws-ebs-csi-driver`):** creates the EBS volumes for the MySQL PVCs. `configurationValues` with `defaultStorageClass.enabled: true` creates a default StorageClass (`ebs-csi-default-sc`). New EKS versions don't come with a default StorageClass and the MySQL chart doesn't set one, so without it the PVCs stay `Pending`.

### `java-app/`

The app reads its DB settings from the env vars `DB_USER`, `DB_PWD`, `DB_SERVER` and `DB_NAME`.

- **`Dockerfile`:** `COPY build/libs/*.jar /opt/app/app.jar` instead of the fixed jar name. The jar name contains the version, and the pipeline changes the version on every build.
- **`build.gradle`:**
  - `jar { enabled = false }`: the Spring Boot plugin builds two jars, the app jar and a `-plain.jar`. The plain jar is only for using the project as a library. Turning it off leaves one jar in `build/libs`, so the wildcard in the Dockerfile matches one file.
  - `version '1.0.0'` instead of `'1.0-SNAPSHOT'`, so the pipeline can split it into major.minor.patch.
  - `options.release = 17` instead of a Java 17 toolchain. The Jenkins container has Java 21 and no Java 17, so the toolchain would fail. With `release = 17` it compiles with Java 21 but the output runs on the `openjdk:17` base image.

### `helm/`

Helm and Helmfile instead of plain YAML files. One `helmfile sync` installs or updates all three releases, and the pipeline only has to pass the image tag.

- **`helmfile.yaml`:** three releases. `mysql` comes from the Bitnami repo, `phpmyadmin` and `java-app` from the local charts. `java-app` goes to namespace `my-app` (Fargate); Helmfile creates the namespace.
- **`values/mysql-values.yaml`:** `architecture: replication` (primary + 1 secondary), root password and database `my-app-db`. The image is `bitnamilegacy/mysql`. `allowInsecureImages: true` is needed so the chart accepts the substituted image.
- **`values/java-app-values.yaml`:** 3 replicas, the ECR image, `appVersion` (the pipeline overrides it). `DB_SERVER: mysql-primary.default` is in `configData`; the app runs in another namespace, so the service name needs `.default`. DB user, password and DB name are in `secretData`.
- **`charts/java-app`:** Deployment, Service (ClusterIP, 8080), ConfigMap `db-config` and Secret `db-secret`. The env vars in the Deployment are generated from the `configData` and `secretData` keys. There are no `imagePullSecrets`: on EKS the node role and the Fargate pod execution role already have read access to ECR.
- **`charts/phpmyadmin`:** Deployment and Service `phpmyadmin-service` (8081 → 80). `PMA_HOST` is `mysql-primary`, and the root password is read from the `mysql` Secret that the MySQL chart creates, so the password is defined in one place.


### `Jenkinsfile`

The job is a Pipeline job (`java-app-eks`): Pipeline script from SCM, branch `*/main`, Script Path `11-eks/02-projects/Jenkinsfile`.

1. **increment version:** reads `build.gradle`, finds the version with `^version '(.+)'` and increases the minor version (`1.0.0` → `1.1.0`).
   - The new version is written back with `replaceFirst` and the same anchored regex.
   - The regex matcher is not kept in a variable: Jenkins can't serialize it and fails if one is in scope when a step like `writeFile` runs.
   - The image tag is `<version>-<BUILD_NUMBER>`. If a build fails after pushing an image, the next build gets a different tag and nothing is overwritten.
2. **build app:** `gradle clean build` in `java-app/`, with the Jenkins Gradle tool `gradle-8`.
3. **build image:** `docker build` with `java-app/` as the build context, then `aws ecr get-login-password | docker login` and `docker push`. A fresh ECR token on every build; a token saved as a Jenkins credential expires after 12 hours.
4. **deploy:** `aws eks update-kubeconfig` creates the kubeconfig on every build, so nothing has to be copied to Jenkins. Then `helmfile sync --set appVersion=<tag>` deploys the new image.
5. **commit version update:** commits only `build.gradle` (`git add .` would also add the `build/` folder) and pushes to `HEAD:main`, the same branch the job builds, so the next build reads the new version. The job is started manually (no webhook), so the version commit doesn't start another build.

## Run

```bash
aws ecr create-repository --repository-name java-app --region eu-central-1
cd eks
eksctl create cluster -f cluster.yaml
```

Then **Build Now** on the Jenkins job. To reach the app and phpMyAdmin:

```bash
kubectl port-forward svc/java-app-service 8080:8080 -n my-app
kubectl port-forward svc/phpmyadmin-service 8081:8081
```

## Result

The cluster was created with the Fargate profile, the managed node group and the add-ons:

```
2026-10-15 09:55:18 [ℹ]  creating EKS cluster "app-cluster" in "eu-central-1" region with Fargate profile and managed nodes
...
2026-10-15 10:12:47 [✔]  created 1 managed nodegroup(s) in cluster "app-cluster"
...
2026-10-15 10:13:59 [ℹ]  addon "aws-ebs-csi-driver" active
...
2026-10-15 10:14:42 [✔]  EKS cluster "app-cluster" in "eu-central-1" region is ready
```

The default StorageClass from the EBS CSI add-on and the Fargate profile:

```
NAME                           PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
ebs-csi-default-sc (default)   ebs.csi.aws.com         Delete          WaitForFirstConsumer   true                   3m56s
gp2                            kubernetes.io/aws-ebs   Delete          WaitForFirstConsumer   false                  16m
```

```
NAME            SELECTOR_NAMESPACE      SELECTOR_LABELS POD_EXECUTION_ROLE_ARN                                                                          SUBNETS             TAGS     STATUS
fp-my-app       my-app                  <none>          arn:aws:iam::731872836472:role/eksctl-app-cluster-cluster-FargatePodExecutionRole-yf3Lx0b2nSZR  subnet-0339770ee47b2e0b1,subnet-0774be6b3cfa0e161,subnet-01bc068cfbf50d659   <none>  ACTIVE
```

The Jenkins pipeline ran all stages:

```
+ gradle clean build
...
BUILD SUCCESSFUL in 1m 2s
...
+ docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-app:1.1.0-2
...
1.1.0-2: digest: sha256:588209231b97ff308a3320eb9e68488cfb22b356f46eac57b3cd259512590278 size: 856
...
+ helmfile sync --set appVersion=1.1.0-2
...
NAME         NAMESPACE   CHART                 VERSION   DURATION
phpmyadmin   default     ./charts/phpmyadmin   0.1.0           5s
java-app     my-app      ./charts/java-app     0.1.0           5s
mysql        default     bitnami/mysql         14.0.3         11s
...
+ git push origin HEAD:main
To https://github.com/emrearabacioglu/devops-bootcamp.git
   ce13501..70db579  HEAD -> main
...
Finished: SUCCESS
```

<img width="1240" height="421" alt="image" src="https://github.com/user-attachments/assets/08f9aebf-149d-4399-b16b-20e127844c6c" />


MySQL and phpMyAdmin run on the EC2 nodes, the three java-app pods on Fargate nodes:

```
NAMESPACE     NAME                                   READY   STATUS    RESTARTS   AGE     IP                NODE                                                       NOMINATED NODE   READINESS GATES
default       mysql-primary-0                        1/1     Running   0          103s    192.168.55.238    ip-192-168-45-243.eu-central-1.compute.internal            <none>           <none>
default       mysql-secondary-0                      1/1     Running   0          103s    192.168.25.117    ip-192-168-29-88.eu-central-1.compute.internal             <none>           <none>
default       phpmyadmin-64fb7bb5b-fnk42             1/1     Running   0          110s    192.168.56.10     ip-192-168-45-243.eu-central-1.compute.internal            <none>           <none>
...
my-app        java-app-deployment-6fbd5b5d44-2j7tf   1/1     Running   0          110s    192.168.108.226   fargate-ip-192-168-108-226.eu-central-1.compute.internal   <none>           <none>
my-app        java-app-deployment-6fbd5b5d44-bdxnz   1/1     Running   0          110s    192.168.137.140   fargate-ip-192-168-137-140.eu-central-1.compute.internal   <none>           <none>
my-app        java-app-deployment-6fbd5b5d44-z57sf   1/1     Running   0          110s    192.168.156.70    fargate-ip-192-168-156-70.eu-central-1.compute.internal    <none>           <none>
```

```
NAME                                                       STATUS   ROLES    AGE   VERSION
fargate-ip-192-168-108-226.eu-central-1.compute.internal   Ready    <none>   73s   v1.34.11-eks-1ccbad1
fargate-ip-192-168-137-140.eu-central-1.compute.internal   Ready    <none>   79s   v1.34.11-eks-1ccbad1
fargate-ip-192-168-156-70.eu-central-1.compute.internal    Ready    <none>   81s   v1.34.11-eks-1ccbad1
ip-192-168-29-88.eu-central-1.compute.internal             Ready    <none>   13m   v1.34.11-eks-b9510e3
ip-192-168-45-243.eu-central-1.compute.internal            Ready    <none>   13m   v1.34.11-eks-b9510e3
```

The MySQL volumes were created from the default StorageClass:

```
NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS         VOLUMEATTRIBUTESCLASS   AGE
data-mysql-primary-0     Bound    pvc-1ca073ac-0ef8-4c6e-829f-6af4488d479c   8Gi        RWO            ebs-csi-default-sc   <unset>                 2m55s
data-mysql-secondary-0   Bound    pvc-e2b0dd37-89cf-43a9-881d-55e29d9eea40   8Gi        RWO            ebs-csi-default-sc   <unset>                 2m55s
```

The Helm releases and the image tag from the pipeline:

```
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                   APP VERSION
java-app        my-app          1               2026-10-15 07:21:49.034117035 +0000 UTC deployed        java-app-0.1.0          1.16.0
mysql           default         1               2026-10-15 07:21:55.395139279 +0000 UTC deployed        mysql-14.0.3            9.4.0
phpmyadmin      default         1               2026-10-15 07:21:49.048712974 +0000 UTC deployed        phpmyadmin-0.1.0
```

```
731872836472.dkr.ecr.eu-central-1.amazonaws.com/java-app:1.1.0-2
```

I opened the app (`localhost:8080`) and phpMyAdmin (`localhost:8081`) in the browser through port-forward; both worked and phpMyAdmin showed the `my-app-db` database.



