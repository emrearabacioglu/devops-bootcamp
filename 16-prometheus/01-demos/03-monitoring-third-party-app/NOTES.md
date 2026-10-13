# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Configure Monitoring for a Third-Party Application

### Demo Executed: Expose Redis Metrics with an Exporter

#### Why an Exporter?
Redis (`redis-cart`, the cart database of the microservices app) doesn't expose metrics in the Prometheus format. An **exporter** runs next to it, connects to Redis, reads its internal stats and exposes them on a `/metrics` endpoint that Prometheus can scrape.

#### How Prometheus Finds Targets
Prometheus finds its targets through **ServiceMonitor** resources. A ServiceMonitor selects a Service by its labels and tells Prometheus which port to scrape. The Helm chart already created one for every component of the stack:

```bash
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get servicemonitor -n monitoring
    NAME                                                 AGE
    monitoring-grafana                                   4h1m
    monitoring-kube-prometheus-alertmanager              4h1m
    monitoring-kube-prometheus-apiserver                 4h1m
    ...
    monitoring-kube-state-metrics                        4h1m
    monitoring-prometheus-node-exporter                  4h1m
```

Like the alert rules, a ServiceMonitor needs the `release: monitoring` label, otherwise the Prometheus instance of the stack ignores it.

#### Install the Redis Exporter with Helm
The `prometheus-redis-exporter` chart is installed from the Prometheus community OCI registry. The values file points the exporter to the Redis service and enables a ServiceMonitor with the `release: monitoring` label:

```yaml
    redisAddress: redis://redis-cart:6379
    serviceMonitor:
      enabled: true
      labels:
        release: monitoring
```

```bash
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get svc | grep redis
    redis-cart              ClusterIP      10.100.129.196   <none>        6379/TCP       4h5m

    root@PC:~/modules/prometheus/03-redis-monitoring# helm install redis-exporter oci://ghcr.io/prometheus-community/charts/prometheus-redis-exporter -f redis-values.yaml
    Pulled: ghcr.io/prometheus-community/charts/prometheus-redis-exporter:6.33.0
    NAME: redis-exporter
    LAST DEPLOYED: Sat Oct 10 13:12:44 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1

    root@PC:~/modules/prometheus/03-redis-monitoring# helm ls
    NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                                   APP VERSION
    redis-exporter  default         1               2026-10-10 13:12:44.934757437 +0300 +03 deployed        prometheus-redis-exporter-6.33.0        v1.93.0

    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get pod | grep redis
    redis-cart-5c6f5bbbd9-5js5m                                 1/1     Running   0          4h13m
    redis-exporter-prometheus-redis-exporter-76fc4969d9-494vq   1/1     Running   0          80s
```

#### The Generated ServiceMonitor
The chart created a ServiceMonitor in the `default` namespace. It selects the exporter's Service by its labels and scrapes the `redis-exporter` port:

```yaml
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get servicemonitor redis-exporter-prometheus-redis-exporter -o yaml
    apiVersion: monitoring.coreos.com/v1
    kind: ServiceMonitor
    metadata:
      labels:
        app.kubernetes.io/managed-by: Helm
        release: monitoring
      name: redis-exporter-prometheus-redis-exporter
      namespace: default
    spec:
      endpoints:
      - port: redis-exporter
      jobLabel: redis-exporter-prometheus-redis-exporter
      namespaceSelector:
        matchNames:
        - default
      selector:
        matchLabels:
          app.kubernetes.io/instance: redis-exporter
          app.kubernetes.io/name: prometheus-redis-exporter
```

<img width="1909" height="381" alt="image" src="https://github.com/user-attachments/assets/0880fa24-261c-4148-9ff7-ef924f643913" />

### Demo Executed: Redis Alert Rules and Grafana Dashboard

#### Alert Rules for Redis
The rules are taken from the [Awesome Prometheus Alerts](https://awesome-prometheus-alerts.grep.to/) collection, which has ready rules for common exporters. They use the metrics exposed by the Redis exporter:

* **`RedisDown`:** `redis_up` is `0` when the exporter can't connect to Redis. It fires immediately.
* **`RedisTooManyConnections`:** connected clients are more than 90% of the `maxclients` limit for 2 minutes.

```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: PrometheusRule
    metadata:
      name: redis-rules
      labels:
        app: kube-prometheus-stack
        release: monitoring
    spec:
      groups:
      - name: redis.rules
        rules:
        - alert: RedisDown
          expr: 'redis_up == 0'
          for: 0m
          labels:
            severity: critical
          annotations:
            summary: Redis down (instance {{ $labels.instance }})
            description: "Redis instance is down\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"

        - alert: RedisTooManyConnections
          expr: 'redis_connected_clients / redis_config_maxclients * 100 > 90 and redis_config_maxclients > 0'
          for: 2m
          labels:
            severity: warning
          annotations:
            summary: Redis too many connections (instance {{ $labels.instance }})
            description: "Redis is running out of connections (> 90% used)\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
```

```bash
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl apply -f redis-rules.yaml
    prometheusrule.monitoring.coreos.com/redis-rules created
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get prometheusrule
    NAME          AGE
    redis-rules   18s
```

The `redis.rules` group appears in the Prometheus UI with both rules `inactive`:

<img width="1900" height="694" alt="image" src="https://github.com/user-attachments/assets/3956d918-b01f-444c-b889-9319c1776bcd" />

#### Trigger RedisDown
To simulate a Redis outage, the `redis-cart` deployment is scaled down to 0 replicas (`replicas: 0` with `kubectl edit`), and then scaled back up to 1:

```bash
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get pod | grep redis
    redis-cart-5c6f5bbbd9-5js5m                                 1/1     Running   0          4h33m
    redis-exporter-prometheus-redis-exporter-76fc4969d9-494vq   1/1     Running   0          21m

    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl edit deployment redis-cart
    deployment.apps/redis-cart edited
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get pod | grep redis
    redis-exporter-prometheus-redis-exporter-76fc4969d9-494vq   1/1     Running   0          22m
```

The exporter is still running but can't reach Redis, so `redis_up` drops to `0` and `RedisDown` fires:

<img width="1905" height="575" alt="image" src="https://github.com/user-attachments/assets/a263b6ca-93da-4bc5-8ae2-4e68c34eb424" />

```bash
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl edit deployment redis-cart
    deployment.apps/redis-cart edited
    root@PC:~/modules/prometheus/03-redis-monitoring# kubectl get pod | grep redis-cart
    redis-cart-5c6f5bbbd9-r86lx                                 0/1     Running   0          6s
```

#### Grafana Dashboard for Redis
Instead of building a dashboard from scratch, a community dashboard made for the Redis exporter is imported from [grafana.com/grafana/dashboards](https://grafana.com/grafana/dashboards): **Dashboards > New > Import**, enter the dashboard ID, and select Prometheus as the data source. It shows uptime, connected clients, memory usage, commands per second and network I/O of the Redis instance:

<img width="1914" height="992" alt="image" src="https://github.com/user-attachments/assets/37befd1d-903d-4801-aabb-9b5b41985d0b" />
