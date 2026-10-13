# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Install a stateful service (MongoDB) on Kubernetes using Helm

### Demo Executed: MongoDB replicaset with Helm on Linode Kubernetes Engine

#### Created K8s cluster on Linode Kubernetes Engine
Created a 2-node cluster on LKE:

<img width="1908" height="353" alt="image" src="https://github.com/user-attachments/assets/93420d43-fef2-4dbd-9540-7e0e7f3958c9" />

Pointed kubectl to the downloaded kubeconfig file and checked the nodes:

    root@PC:~/helm# export KUBECONFIG=test-kubeconfig.yaml
    root@PC:~/helm# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645862-950499-d6sh5   Ready    <none>   3m31s   v1.36.2
    lke645862-950499-rx6k6   Ready    <none>   3m19s   v1.36.2

#### Deployed replicated MongoDB (StatefulSet using Helm Chart) and configured Data Persistence with Linode Block Storage
Installed Helm and added the Bitnami repo:

    root@PC:~/helm# curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 | bash
    root@PC:~/helm# helm repo add bitnami https://charts.bitnami.com/bitnami
    "bitnami" has been added to your repositories

Values file: 3 replicas, Linode block storage for the volumes, and the root password:

    root@PC:~/helm# cat helm-mongodb.yaml
    architecture: replicaset
    replicaCount: 3
    persistence:
      storageClass: "linode-block-storage"
    auth:
      rootPassword: secret-root-pwd

Installed the chart with this values file:

    root@PC:~/helm# helm install mongodb --values helm-mongodb.yaml bitnami/mongodb
    NAME: mongodb
    LAST DEPLOYED: Thu Aug 20 14:17:28 2026
    NAMESPACE: default
    STATUS: deployed

MongoDB runs as a StatefulSet with 3 pods plus an arbiter:

    root@PC:~/helm# kubectl get all
    NAME                    READY   STATUS    RESTARTS   AGE
    pod/mongodb-0           1/1     Running   0          4m
    pod/mongodb-1           1/1     Running   0          3m5s
    pod/mongodb-2           1/1     Running   0          117s
    pod/mongodb-arbiter-0   1/1     Running   0          4m
    
    NAME                               READY   AGE
    statefulset.apps/mongodb           3/3     4m
    statefulset.apps/mongodb-arbiter   1/1     4m

#### Deployed MongoExpress (Deployment and Service)
Mongo Express takes the root password from the `mongodb` Secret created by the chart and connects to `mongodb-0.mongodb-headless`:

    root@PC:~/helm# cat helm-mongo-express.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mongo-express
      labels:
        app: mongo-express
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mongo-express
      template:
        metadata:
          labels:
            app: mongo-express
        spec:
          containers:
          - name: mongo-express
            image: mongo-express
            ports:
            - containerPort: 8081
            env:
            - name: ME_CONFIG_MONGODB_ADMINUSERNAME
              value: root
            - name: ME_CONFIG_MONGODB_ADMINPASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb
                  key: mongodb-root-password
            - name: ME_CONFIG_MONGODB_URL
              value: "mongodb://$(ME_CONFIG_MONGODB_ADMINUSERNAME):$(ME_CONFIG_MONGODB_ADMINPASSWORD)@mongodb-0.mongodb-headless:27017"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongo-express-service
    spec:
      selector:
        app: mongo-express
      ports:
        - protocol: TCP
          port: 8081
          targetPort: 8081

Applied it and checked the logs:

    root@PC:~/helm# kubectl apply -f helm-mongo-express.yaml
    deployment.apps/mongo-express created
    service/mongo-express-service created
    
    root@PC:~/helm# kubectl logs mongo-express-794fb84c64-k4lk2
    Waiting for mongodb-0.mongodb-headless:27017...
    No custom config.js found, loading config.default.js
    Welcome to mongo-express 1.0.2
    ------------------------
    Mongo Express server listening at http://0.0.0.0:8081

#### Deployed NGINX Ingress Controller as Loadbalancer (using Helm Chart)
Installed the NGINX Ingress Controller chart from its OCI registry. Its service got the external IP `85.90.246.91`:

    root@PC:~/helm# helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress --set controller.reportIngressStatus.enable=true
    NAME: nginx-ingress
    LAST DEPLOYED: Thu Aug 20 14:32:48 2026
    NAMESPACE: default
    STATUS: deployed
    
    root@PC:~/helm# kubectl get svc
    NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)                      AGE
    nginx-ingress-controller   LoadBalancer   10.128.86.169    85.90.246.91   80:32260/TCP,443:31566/TCP   2m9s

#### Configured Ingress rule
Ingress rule that sends requests for the Linode host name to `mongo-express-service`:

    root@PC:~/helm# cat helm-ingress-yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
        name: mongo-express
    spec:
      ingressClassName: nginx-ingress
      rules:
      - host: 85-90-246-91.ip.linodeusercontent.com
        http:
          paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: mongo-express-service
                  port:
                    number: 8081

Applied it:

    root@PC:~/helm# kubectl apply -f helm-ingress-yaml
    ingress.networking.k8s.io/mongo-express created
    
    root@PC:~/helm# kubectl get ingress
    NAME            CLASS           HOSTS                                   ADDRESS   PORTS   AGE
    mongo-express   nginx-ingress   85-90-246-91.ip.linodeusercontent.com             80      10s

#### Connected via browser
Opened Mongo Express in the browser through the Ingress and logged in with the default credentials:

<img width="1895" height="981" alt="image" src="https://github.com/user-attachments/assets/37b85b84-fded-4549-8632-4e10a7b69687" />
