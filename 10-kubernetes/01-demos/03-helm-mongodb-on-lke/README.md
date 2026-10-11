# Install a stateful service (MongoDB) on Kubernetes using Helm

**Technologies:** K8s, Helm, MongoDB, Mongo Express, Linode LKE, Linux

I installed a replicated MongoDB with a Helm chart on a Linode Kubernetes Engine (LKE) cluster, with Linode block storage for the data, and made Mongo Express reachable from the browser through an NGINX Ingress.

## Summary
- Created a 2-node cluster on LKE and pointed kubectl to its kubeconfig (`test-kubeconfig.yaml`, token and certificate replaced with `***`).
- Installed MongoDB with the Bitnami Helm chart. `helm-mongodb.yaml` overrides the chart values: `replicaset` architecture, 3 replicas, `linode-block-storage` storage class and the root password.
- `helm-mongo-express.yaml` has the Mongo Express Deployment and Service. It takes the root password from the `mongodb` Secret created by the chart and connects to `mongodb-0.mongodb-headless:27017`.
- Installed the NGINX Ingress Controller with Helm. Its LoadBalancer service got the external IP `85.90.246.91`.
- `helm-ingress.yaml` is the Ingress rule that sends requests for the Linode host name `85-90-246-91.ip.linodeusercontent.com` to `mongo-express-service`.

## Run
```bash
export KUBECONFIG=test-kubeconfig.yaml
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install mongodb --values helm-mongodb.yaml bitnami/mongodb
kubectl apply -f helm-mongo-express.yaml
helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress --set controller.reportIngressStatus.enable=true
kubectl apply -f helm-ingress.yaml
```

## Result
MongoDB runs as a StatefulSet with 3 pods plus an arbiter, and the Ingress points to Mongo Express. After that Mongo Express opened in the browser on the Ingress host name.
```
root@PC:~/helm# kubectl get all
NAME                    READY   STATUS    RESTARTS   AGE
pod/mongodb-0           1/1     Running   0          4m
pod/mongodb-1           1/1     Running   0          3m5s
pod/mongodb-2           1/1     Running   0          117s
pod/mongodb-arbiter-0   1/1     Running   0          4m
...
root@PC:~/helm# kubectl get ingress
NAME            CLASS           HOSTS                                   ADDRESS   PORTS   AGE
mongo-express   nginx-ingress   85-90-246-91.ip.linodeusercontent.com             80      10s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
