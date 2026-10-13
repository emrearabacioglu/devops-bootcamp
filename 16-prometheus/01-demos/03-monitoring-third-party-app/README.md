# Configure Monitoring for a Third-Party Application

**Technologies:** Prometheus, Kubernetes, Redis, Helm, Grafana

I monitored Redis (`redis-cart`, the cart database of the microservices app) with the Redis exporter, added alert rules for it and imported a Redis dashboard into Grafana.

## Summary
1. Redis was already running in the cluster as `redis-cart` (from the microservices app in `01-install-prometheus-stack`).
2. Installed the `prometheus-redis-exporter` Helm chart with `redis-values.yaml`. The values point the exporter to `redis://redis-cart:6379` and enable a ServiceMonitor with the `release: monitoring` label, so Prometheus scrapes the exporter.
3. Wrote `redis-rules.yaml`, a `PrometheusRule` with two rules from Awesome Prometheus Alerts:
   - `RedisDown`: `redis_up == 0`, fires immediately.
   - `RedisTooManyConnections`: connected clients over 90% of `maxclients` for 2 minutes.
4. Tested `RedisDown` by scaling `redis-cart` to 0 replicas with `kubectl edit`. The alert fired in the Prometheus UI, then I scaled it back to 1.
5. Imported a community Redis exporter dashboard in Grafana (**Dashboards > New > Import**, Prometheus as data source).

## Run
```bash
helm install redis-exporter oci://ghcr.io/prometheus-community/charts/prometheus-redis-exporter -f redis-values.yaml
kubectl apply -f redis-rules.yaml
```

## Result
The exporter is deployed next to Redis and the rules are created:
```
root@PC:~/modules/prometheus/03-redis-monitoring# helm ls
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                                   APP VERSION
redis-exporter  default         1               2026-10-10 13:12:44.934757437 +0300 +03 deployed        prometheus-redis-exporter-6.33.0        v1.93.0

root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get pod | grep redis
redis-cart-5c6f5bbbd9-5js5m                                 1/1     Running   0          4h13m
redis-exporter-prometheus-redis-exporter-76fc4969d9-494vq   1/1     Running   0          80s
...
root@PC:~/modules/prometheus/03-redis-monitoring# kubectl apply -f redis-rules.yaml
prometheusrule.monitoring.coreos.com/redis-rules created
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
