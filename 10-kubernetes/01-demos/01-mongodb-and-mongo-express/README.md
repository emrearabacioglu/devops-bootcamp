# Deploy MongoDB and Mongo Express into local K8s cluster

**Technologies:** Kubernetes, Docker, MongoDB, Mongo Express

I deployed MongoDB and Mongo Express on a local Minikube cluster. The MongoDB credentials are in a Secret and the database URL is in a ConfigMap.

## Summary
- Encoded the demo username and password with base64 and put them into a Secret (`mongo-secret.yaml`).
- `mongo.yaml` has the MongoDB Deployment and an internal (ClusterIP) Service. The root username and password come from the Secret.
- `mongo-configmap.yaml` holds the database URL (`mongodb-service:27017`).
- `mongo-express.yaml` has the Mongo Express Deployment, which reads the credentials from the Secret and the DB URL from the ConfigMap, and a `LoadBalancer` Service with `nodePort: 30000`.
- Applied the Secret and ConfigMap before the Deployments that use them, checked the logs and opened Mongo Express in the browser with `minikube service`.

## Run
```bash
minikube start
kubectl apply -f mongo-secret.yaml
kubectl apply -f mongo.yaml
kubectl apply -f mongo-configmap.yaml
kubectl apply -f mongo-express.yaml
minikube service mongo-express-service
```

## Result
MongoDB pod is running and Mongo Express connected to `mongodb-service:27017`:
```
root@PC:~# kubectl get pod -o wide
NAME                                 READY   STATUS    RESTARTS   AGE    IP            NODE       NOMINATED NODE   READINESS GATES
mongodb-deployment-df5cd6568-5gp67   1/1     Running   0          7m5s   10.244.0.10   minikube   <none>           <none>
...
root@PC:~# kubectl logs mongo-express-5747d566b9-wz2t6
Waiting for mongodb-service:27017...
Welcome to mongo-express 1.0.2
------------------------
Mongo Express server listening at http://0.0.0.0:8081
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
