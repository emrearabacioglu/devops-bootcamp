# Deploy Microservices application in Kubernetes with Production & Security Best Practices

**Technologies:** Kubernetes, Redis, Linux, Linode LKE

I deployed the online shop microservices (Google's "Online Boutique" demo) to a 3-node Linode LKE cluster. All Deployments and Services are in one file, `config.yaml`.

## Summary
- Created a 3-node cluster on LKE, made the kubeconfig file read-only (`chmod 400`) and exported it as `KUBECONFIG`.
- Wrote `config.yaml` with a Deployment and a Service for each of the 11 services (10 app services plus `redis-cart` for the cart service).
- Best practices in the file:
  - fixed image tags (`v0.8.0`, `redis:alpine`), no `latest`
  - `livenessProbe` and `readinessProbe` for every container (gRPC, TCP or HTTP)
  - `replicas: 2` for most Deployments
  - CPU and memory `requests` and `limits` (emailservice, adservice, redis-cart)
  - no NodePort: backend services are `ClusterIP`, only the frontend is a `LoadBalancer`
- Created a `microservices` namespace and applied the file there, then opened the shop in the browser on the frontend's external IP.

## Run
```bash
export KUBECONFIG=~/microservices/online-shop-microservices-kubeconfig.yaml
kubectl create ns microservices
kubectl apply -f config.yaml -n microservices
kubectl get pod -n microservices
kubectl get svc -n microservices
```

## Result
The pods are running and only the frontend has an external IP:
```
root@PC:~/microservices# kubectl get pod -n microservices
NAME                                     READY   STATUS    RESTARTS      AGE
adservice-7dcbd647b4-dgpsh               1/1     Running   0             61s
cartservice-75cd7bb67b-65z46             1/1     Running   0             60s
checkoutservice-7879b466b9-v9bjq         1/1     Running   0             60s
...
redis-cart-6448465667-kfjqh              1/1     Running   0             60s
...
root@PC:~/microservices# kubectl get svc -n microservices
NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)        AGE
...
frontend                LoadBalancer   10.128.45.166    139.162.172.76   80:32023/TCP   84s
paymentservice          ClusterIP      10.128.229.163   <none>           50051/TCP      86s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
