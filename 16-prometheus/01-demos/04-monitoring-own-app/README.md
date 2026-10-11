# Configure Monitoring for Own Application

**Technologies:** Prometheus, Kubernetes, Node.js, Grafana, Docker, Docker Hub

I added Prometheus metrics to a Node.js app with the `prom-client` library, deployed it to the cluster and made Prometheus scrape it. Then I built a Grafana dashboard for these metrics.

## Summary
1. The app in `nodejs-app-monitoring/app/server.js` uses `prom-client` to count HTTP requests (`http_request_operations_total`), measure their duration (`http_request_duration_seconds` histogram) and expose them on `/metrics`.
2. Built the image from `nodejs-app-monitoring/Dockerfile` and pushed it to my private Docker Hub repo `emrearabacioglu/demo-app:nodeapp`. I changed the base image to `node:20-alpine` because the current `prom-client` needs a newer Node.js.
3. Created the `my-registry-key` docker-registry Secret so the cluster can pull from the private repo.
4. `nodejs-app-monitoring/k8s-config.yaml` has the Deployment (port `3000`, `imagePullSecrets`), a `ClusterIP` Service with the port named `service`, and a ServiceMonitor that selects the Service by `app: nodeapp` and scrapes `/metrics`. The ServiceMonitor has the `release: monitoring` label so Prometheus picks it up.
5. Created a Grafana dashboard with two panels: `rate(http_request_operations_total[2m])` and `rate(http_request_duration_seconds_sum[2m])`.

## Run
```bash
kubectl create secret docker-registry my-registry-key \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=emrearabacioglu \
  --docker-password='***'
kubectl apply -f k8s-config.yaml
```

## Result
In the Prometheus UI the target `serviceMonitor/default/monitoring-node-app/0` was `UP`, the `http_request_operations_total` metric could be queried, and after sending requests to the app the spikes showed up on both Grafana panels.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
