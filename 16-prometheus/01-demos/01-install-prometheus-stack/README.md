# Install Prometheus Stack in Kubernetes

**Technologies:** Prometheus, Kubernetes, Helm, AWS EKS, eksctl, Grafana, Linux

I created an EKS cluster with eksctl, deployed a microservices app into it and installed Prometheus, Alertmanager and Grafana with the `kube-prometheus-stack` Helm chart (Prometheus Operator).

## Summary
1. Created the EKS cluster with `eksctl create cluster` using the default settings (new VPC, managed node group with 2 nodes, region `eu-central-1`).
2. Deployed the Online Boutique microservices app (11 services and a Redis cart) into the `default` namespace with `config-microservices.yaml`. This is the app that is monitored in this module.
3. Installed `prometheus-community/kube-prometheus-stack` with Helm into a separate `monitoring` namespace. It runs the Operator, Prometheus, Alertmanager, Grafana, kube-state-metrics and node-exporter.
4. Saved the `kubectl describe` outputs of the Prometheus and Alertmanager StatefulSets and the Operator Deployment to `prom.yaml`, `alert.yaml` and `operator.yaml`, to see how they are configured. These are not manifests to apply.
5. Opened the Prometheus UI and Grafana with `kubectl port-forward` and checked the scrape targets and the default dashboards.
6. Created load on the `frontend` service from a temporary curl pod and saw the CPU spike in the **Kubernetes / Compute Resources / Cluster** dashboard. The course image `radial/busyboxplus:curl` doesn't run on the current EKS nodes, so I used `curlimages/curl`.

## Run
```bash
eksctl create cluster
kubectl apply -f config-microservices.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
kubectl port-forward service/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 &
kubectl port-forward service/monitoring-grafana -n monitoring 8080:80 &
```

## Result
All components of the stack are running in the `monitoring` namespace:
```
root@PC:~/modules/prometheus/01-prometheus-stack# kubectl get all -n monitoring
NAME                                                         READY   STATUS    RESTARTS   AGE
pod/alertmanager-monitoring-kube-prometheus-alertmanager-0   2/2     Running   0          98s
pod/monitoring-grafana-867956469b-hrwmq                      3/3     Running   0          104s
pod/monitoring-kube-prometheus-operator-8555d4668d-zzmtz     1/1     Running   0          104s
pod/monitoring-kube-state-metrics-7b5bd68446-dt4np           1/1     Running   0          104s
pod/monitoring-prometheus-node-exporter-2p5zb                1/1     Running   0          104s
pod/monitoring-prometheus-node-exporter-m6tt6                1/1     Running   0          104s
pod/prometheus-monitoring-kube-prometheus-prometheus-0       2/2     Running   0          98s
...
NAME                                                                    READY   AGE
statefulset.apps/alertmanager-monitoring-kube-prometheus-alertmanager   1/1     99s
statefulset.apps/prometheus-monitoring-kube-prometheus-prometheus       1/1     99s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
