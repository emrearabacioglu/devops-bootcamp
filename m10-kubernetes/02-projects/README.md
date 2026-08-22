### Exercises for Module "Container Orchestration with Kubernetes"

**Business Case:** Your company’s java-mysql application is running with docker-compose on a server. This application is used often internally and by your company clients too. You noticed that the server isn't very stable: Often a database container dies or the application itself, or docker daemon must be restarted. During this time people can't access the app!

So when this happens, the users write to you to tell you that the app is down and ask you to fix it. You SSH into the server, restart the containers with docker-compose and containers start again.

But this is annoying work, plus it doesn't look good for your company that your clients often can't access the app. So you want to make your application more reliable and highly available. You want to replicate both the database and the app, so if one container goes down, there is always a backup. Also you don't want to rely on a single server, but have multiple, in case 1 whole server goes down or gets rebooted etc.



So you look into different solutions and decide to use the container orchestration tool Kubernetes to solve the issue. For now you want to configure it and deploy your application manually, since it's a new tool and want to try it out manually before automating.

******

<details>
<summary>EXERCISE 1: Create a Kubernetes cluster</summary>
 <br />
  
 **Objectives:**
 
* Create a Kubernetes cluster (Minikube or LKE)

↳ **Execution:**

<img width="2983" height="1447" alt="image" src="https://github.com/user-attachments/assets/64b6e3b3-93de-464a-9374-293358fbd953" />

Terminal: 
```bash
root@PC:~/k8s-exercises# ll
total 12
drwxr-xr-x  2 root root 4096 Aug 22 14:55 ./
drwx------ 15 root root 4096 Aug 22 14:38 ../
-rwxrwxrwx  1 root root 2825 Aug 22 14:55 my-app-kubeconfig.yaml*
root@PC:~/k8s-exercises# chmod 400 my-app-kubeconfig.yaml
root@PC:~/k8s-exercises# export KUBECONFIG=~/k8s-exercises/my-app-kubeconfig.yaml
root@PC:~/k8s-exercises# kubectl get nodes
NAME                     STATUS   ROLES    AGE     VERSION
lke646525-951914-8mxxq   Ready    <none>   4m32s   v1.36.2
lke646525-951914-h49qp   Ready    <none>   4m30s   v1.36.2
lke646525-951914-lhv7t   Ready    <none>   4m34s   v1.36.2

```



</details>

******

<details>
<summary>EXERCISE 2: Deploy Mysql with 2 replicas</summary>
 <br />
  
 **Objectives:**
 
* Deploy Mysql database with 2 replicas and volumes for data persistence

↳ **Execution:**

```bash
root@PC:~/k8s-exercises# helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" already exists with the same configuration, skipping
root@PC:~/k8s-exercises# helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈
root@PC:~/k8s-exercises# nano mysql-values.yaml
root@PC:~/k8s-exercises# nano mysql-values.yaml
root@PC:~/k8s-exercises# cat my
my-app-kubeconfig.yaml  mysql-values.yaml
root@PC:~/k8s-exercises# cat mysql-values.yaml
global:
  security:
    allowInsecureImages: True
image:
  registry: docker.io
  tag: latest
  repository: bitnamilegacy/mysql
architecture: replication
secondary:
  replicaCount: 1
root@PC:~/k8s-exercises# helm install mysql bitnami/mysql -f mysql-values.yaml
NAME: mysql
LAST DEPLOYED: Sat Aug 22 15:09:24 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: mysql
CHART VERSION: 14.0.3
APP VERSION: 9.4.0

⚠ WARNING: Since August 28th, 2025, only a limited subset of images/charts are available for free.
    Subscribe to Bitnami Secure Images to receive continued support and security updates.
    More info at https://bitnami.com and https://github.com/bitnami/containers/issues/83267

** Please be patient while the chart is being deployed **

Tip:

  Watch the deployment status using the command: kubectl get pods -w --namespace default

Services:

  echo Primary: mysql-primary.default.svc.cluster.local:3306
  echo Secondary: mysql-secondary.default.svc.cluster.local:3306

Execute the following to get the administrator credentials:

  echo Username: root
  MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace default mysql -o jsonpath="{.data.mysql-root-password}" | base64 -d)

To connect to your database:

  1. Run a pod that you can use as a client:

      kubectl run mysql-client --rm --tty -i --restart='Never' --image  docker.io/bitnamilegacy/mysql:latest --namespace default --env MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --command -- bash

  2. To connect to primary service (read/write):

      mysql -h mysql-primary.default.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD"

  3. To connect to secondary service (read-only):

      mysql -h mysql-secondary.default.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD"






WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - primary.resources
  - secondary.resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

⚠ SECURITY WARNING: Original containers have been substituted. This Helm chart was designed, tested, and validated on multiple platforms using a specific set of Bitnami and Tanzu Application Catalog containers. Substituting other containers is likely to cause degraded security and performance, broken chart features, and missing environment variables.

Substituted images detected:
  - docker.io/bitnamilegacy/mysql:latest

⚠ SECURITY WARNING: Verifying original container images was skipped. Please note this Helm chart was designed, tested, and validated on multiple platforms using a specific set of Bitnami and Bitnami Secure Images containers. Substituting other containers is likely to cause degraded security and performance, broken chart features, and missing environment variables.
root@PC:~/k8s-exercises# kubectl get pods
NAME                READY   STATUS    RESTARTS   AGE
mysql-primary-0     0/1     Running   0          56s
mysql-secondary-0   0/1     Running   0          56s

```

</details>

******

<details>
<summary>EXERCISE 3: Deploy your Java Application with 2 replicas</summary>
 <br />
  
 **Objectives:**
 
* Deploy the Java application with 2 replicas - note: once you have pushed your image to docker hub, you will need to ensure you are using this image name and tag in your application's configuration

  With docker-compose, you were setting env_vars on the server. In K8s there are separate components for that, so you want to:

* Create ConfigMap and Secret with the correct values and reference them in the application deployment config file.

↳ **Execution:**

```bash
root@PC:~/k8s-exercises# cat db-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  db_server: mysql-primary.default

root@PC:~/k8s-exercises# DOCKER_REGISTRY_SERVER=docker.io
root@PC:~/k8s-exercises# DOCKER_USER=emrearabacioglu
root@PC:~/k8s-exercises# DOCKER_EMAIL=emrearabacolu@gmail.com
root@PC:~/k8s-exercises# DOCKER_PASSWORD=Docker.123

root@PC:~/k8s-exercises# export KUBECONFIG=~/k8s-exercises/my-app-kubeconfig.yaml

root@PC:~/k8s-exercises# kubectl create secret docker-registry my-registry-key \
  --docker-server=$DOCKER_REGISTRY_SERVER \
  --docker-username=$DOCKER_USER \
  --docker-password=$DOCKER_PASSWORD \
  --docker-email=$DOCKER_EMAIL
secret/my-registry-key created

root@PC:~/k8s-exercises# cat java-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-app-deployment
  labels:
    app: java-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: java-app
  template:
    metadata:
      labels:
        app: java-app
    spec:
      imagePullSecrets:
      - name: my-registry-key
      containers:
      - name: javamysqlapp
        image: emrearabacioglu/java-app:v1
        ports:
        - containerPort: 8080
        env:
         - name: DB_USER
           valueFrom:
             secretKeyRef:
               name: db-secret
               key: db_user
         - name: DB_PWD
           valueFrom:
             secretKeyRef:
               name: db-secret
               key: db_pwd
         - name: DB_NAME
           valueFrom:
             secretKeyRef:
               name: db-secret
               key: db_name
         - name: DB_SERVER
           valueFrom:
             configMapKeyRef:
              name: db-config
              key: db_server
---
apiVersion: v1
kind: Service
metadata:
  name: java-app-service
spec:
  selector:
    app: java-app
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080

root@PC:~/k8s-exercises# kubectl apply -f db-secret.yaml
secret/db-secret configured

root@PC:~/k8s-exercises# kubectl apply -f db-config.yaml
configmap/db-config created

root@PC:~/k8s-exercises# kubectl apply -f java-app.yaml
deployment.apps/java-app-deployment created
service/java-app-service created

root@PC:~/k8s-exercises# kubectl get pod
NAME                                   READY   STATUS    RESTARTS   AGE
java-app-deployment-546fbb8576-bn7d9   1/1     Running   0          67s
java-app-deployment-546fbb8576-pd7x6   1/1     Running   0          67s
java-app-deployment-546fbb8576-q2x9g   1/1     Running   0          67s
mysql-primary-0                        1/1     Running   0          162m
mysql-secondary-0                      1/1     Running   0          162m

root@PC:~/k8s-exercises# kubectl get svc
NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
java-app-service           ClusterIP   10.128.87.110   <none>        8080/TCP   4m19s
kubernetes                 ClusterIP   10.128.0.1      <none>        443/TCP    152m
mysql-primary              ClusterIP   10.128.18.4     <none>        3306/TCP   135m
mysql-primary-headless     ClusterIP   None            <none>        3306/TCP   135m
mysql-secondary            ClusterIP   10.128.152.180  <none>        3306/TCP   135m
mysql-secondary-headless   ClusterIP   None            <none>        3306/TCP   135m

root@PC:~/k8s-exercises# kubectl logs -l app=java-app --tail=15
2026-08-22T14:50:39.165Z  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2026-08-22T14:50:39.171Z  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 1279 ms
2026-08-22T14:50:39.815Z  INFO 1 --- [           main] com.example.Application                  : Java app started
2026-08-22T14:50:39.968Z  INFO 1 --- [           main] o.s.b.a.w.s.WelcomePageHandlerMapping    : Adding welcome page: class path resource [static/index.html]
2026-08-22T14:50:40.352Z  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
2026-08-22T14:50:40.369Z  INFO 1 --- [           main] com.example.Application                  : Started Application in 3.007 seconds (process running for 3.579)

```


</details>

******

<details>
<summary>EXERCISE 4: Deploy phpmyadmin</summary>
 <br />
  
 **Objectives:**
 
* Deploy phpmyadmin to access Mysql UI.
For this deployment you just need 1 replica, since this is only for your own use, so it doesn't have to be Highly Available. A simple deployment.yaml file and internal service will be enough.
↳ **Execution:**


</details>

******

Now your application setup is running in the cluster, but you still need a proper way to access the application. Also, you don't want users to access the application using the IP address but instead to use a domain name. For that, you want to install Ingress controller in the cluster and configure ingress access for your application.


******

<details>
<summary>EXERCISE 5: Deploy Ingress Controller</summary>
 <br />
  
 **Objectives:**
 
* Deploy Ingress Controller in the cluster - using Helm

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 6: Create Ingress rule</summary>
 <br />
  
 **Objectives:**
 
* Create an Ingress rule for your application’s access
  If you are using Minikube, the application must be accessible on my-java-app.com
  For LKE, use the Linode node-balancer address - line 48 of the Index.html file for the application must be updated to include the address

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 7: Port-forward for phpmyadmin</summary>
 <br />

  However, you don't want to expose phpmyadmin for security reasons. So you configure port-forwarding for the service to access on localhost, whenever you need it.

 **Objectives:**
 
* Configure port-forwarding for phpmyadmin

↳ **Execution:**


</details>

******

<details>
<summary>EXERCISE 8: Create Helm Chart for Java App</summary>
 <br />

  As the final step, you decide to create a helm chart for your Java application where all the configuration files are configurable. You can then tell developers how they can use it by setting all the chart values. This chart will be hosted in its own git repository.
  
 **Objectives:**
 
* All config files: service, deployment, ingress, configMap, secret, will be part of the chart

↳ **Execution:**

* Create custom values file as an example for developers to use when deploying the application

↳ **Execution:**

* Deploy the java application using the chart with helmfile

↳ **Execution:**

* Host the chart in its own git repository

↳ **Execution:**


</details>

******
