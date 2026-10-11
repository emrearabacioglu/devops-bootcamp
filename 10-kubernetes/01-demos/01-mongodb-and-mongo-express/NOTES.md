# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy MongoDB and Mongo Express into local K8s cluster

### Demo Executed: MongoDB and Mongo Express on Minikube

#### Created Secret for Mongo Credentials
Encoded the demo username and password with base64 and put them in a Secret:

```bash
    root@PC:~# echo -n 'username' | base64
    dXNlcm5hbWU=
    root@PC:~# echo -n 'password' | base64
    cGFzc3dvcmQ=
    root@PC:~# cat mongo-secret.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: mongodb-secret
    type: Opaque
    data:
      mongo-root-username: dXNlcm5hbWU=
      mongo-root-password: cGFzc3dvcmQ=
    root@PC:~# kubectl apply -f mongo-secret.yaml
    secret/mongodb-secret created
    root@PC:~# kubectl get secret
    NAME             TYPE     DATA   AGE
    mongodb-secret   Opaque   2      10s
```

#### Created MongoDB Deployment & Internal Service
Deployment and internal (ClusterIP) Service for MongoDB in one file, separated by `---`. The root username and password come from the Secret:

```bash
    root@PC:~# cat mongo.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mongodb-deployment
      labels:
        app: mongodb
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mongodb
      template:
        metadata:
          labels:
            app: mongodb
        spec:
          containers:
          - name: mongodb
            image: mongo
            ports:
            - containerPort: 27017
            env:
            - name: MONGO_INITDB_ROOT_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: MONGO_INITDB_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongodb-service
    spec:
      selector:
        app: mongodb
      ports:
      - protocol: TCP
        port: 27017
        targetPort: 27017
    root@PC:~# kubectl apply -f mongo.yaml
    deployment.apps/mongodb-deployment created
    service/mongodb-service created
    root@PC:~# kubectl get pod -o wide
    NAME                                 READY   STATUS    RESTARTS   AGE    IP            NODE       NOMINATED NODE   READINESS GATES
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   0          7m5s   10.244.0.10   minikube   <none>           <none>
    root@PC:~# kubectl get service
    NAME              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)     AGE
    mongodb-service   ClusterIP   10.100.190.116   <none>        27017/TCP   25s
```

#### Created ConfigMap for DB Server URL
ConfigMap with the MongoDB service address:

```bash
    root@PC:~# cat mongo-configmap.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: mongodb-configmap
    data:
      database_url: "mongodb-service:27017"
    root@PC:~# kubectl apply -f mongo-configmap.yaml
    configmap/mongodb-configmap created
```

#### Created MongoExpress Deployment & External Service
Mongo Express gets the credentials from the Secret and the DB address from the ConfigMap. The Service is `LoadBalancer` type with `nodePort: 30000`:

```bash
    root@PC:~# cat mongo-express.yaml
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
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: ME_CONFIG_MONGODB_ADMINPASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
            - name: DATABASE_URL
              valueFrom:
                configMapKeyRef:
                  name: mongodb-configmap
                  key: database_url
            - name: ME_CONFIG_MONGODB_URL
              value: "mongodb://$(ME_CONFIG_MONGODB_ADMINUSERNAME):$(ME_CONFIG_MONGODB_ADMINPASSWORD)@$(DATABASE_URL)"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mongo-express-service
    spec:
      selector:
        app: mongo-express
      type: LoadBalancer
      ports:
      - protocol: TCP
        port: 8081
        targetPort: 8081
        nodePort: 30000
```

Applied it and checked the logs. Mongo Express connected to `mongodb-service:27017`:

```bash
    root@PC:~# kubectl apply -f mongo-express.yaml
    deployment.apps/mongo-express created
    service/mongo-express-service created
    root@PC:~# kubectl logs mongo-express-5747d566b9-wz2t6
    Waiting for mongodb-service:27017...
    Welcome to mongo-express 1.0.2
    ------------------------
    Mongo Express server listening at http://0.0.0.0:8081
```

Opened the service from the host with a Minikube tunnel:

```bash
    root@PC:~# minikube service mongo-express-service
    🔗  Starting tunnel for service mongo-express-service.
    🎉  Opening service default/mongo-express-service in default browser...
    👉  http://127.0.0.1:39985
```

<img width="1699" height="1086" alt="image" src="https://github.com/user-attachments/assets/59666c81-3768-488a-a9bb-da1b26c93a9f" />
