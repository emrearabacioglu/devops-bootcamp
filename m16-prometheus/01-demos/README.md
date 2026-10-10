******

<details>
<summary>Install Prometheus Stack in Kubernetes</summary>
 <br />

### Demo Executed: EKS Cluster with a Microservices App and the Prometheus Stack

#### EKS Cluster with eksctl
The cluster is created with `eksctl` using the default settings: a new VPC, the EKS control plane and a managed node group with 2 nodes. `eksctl` creates everything with CloudFormation stacks and writes the kubeconfig automatically.

```bash
    root@PC:~/modules/prometheus# eksctl create cluster
    ...
    2026-10-09 18:36:27 [✔]  saved kubeconfig as "/root/.kube/config"
    2026-10-09 18:36:27 [✔]  all EKS cluster resources for "attractive-sheepdog-1791559399" have been created
    2026-10-09 18:36:28 [ℹ]  node "ip-192-168-22-208.eu-central-1.compute.internal" is ready
    2026-10-09 18:36:28 [ℹ]  node "ip-192-168-58-113.eu-central-1.compute.internal" is ready
    2026-10-09 18:36:28 [✔]  created 1 managed nodegroup(s) in cluster "attractive-sheepdog-1791559399"
    2026-10-09 18:36:29 [✔]  EKS cluster "attractive-sheepdog-1791559399" in "eu-central-1" region is ready

    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl get nodes
    NAME                                              STATUS   ROLES    AGE     VERSION
    ip-192-168-22-208.eu-central-1.compute.internal   Ready    <none>   4m21s   v1.34.11-eks-3b4a6ca
    ip-192-168-58-113.eu-central-1.compute.internal   Ready    <none>   4m21s   v1.34.11-eks-3b4a6ca
```

#### Microservices Application
The Online Boutique microservices app (11 services and a Redis cart) is deployed into the `default` namespace. It is the application that will be monitored in the next demos.

```bash
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl apply -f config-microservices.yaml
    deployment.apps/emailservice created
    service/emailservice created
    deployment.apps/recommendationservice created
    service/recommendationservice created
    ...
    deployment.apps/frontend created
    service/frontend created
    service/frontend-external created
    deployment.apps/redis-cart created
    service/redis-cart created
```

#### Prometheus Stack with Helm
The `kube-prometheus-stack` chart installs the whole monitoring stack in a separate `monitoring` namespace:

```bash
    root@PC:~/modules/prometheus/01-prometheus-stack# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    root@PC:~/modules/prometheus/01-prometheus-stack# helm repo update
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl create namespace monitoring
    root@PC:~/modules/prometheus/01-prometheus-stack# helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
    NAME: monitoring
    LAST DEPLOYED: Fri Oct  9 18:44:08 2026
    NAMESPACE: monitoring
    STATUS: deployed
    REVISION: 1
```

#### Explore the Deployed Stack
```bash
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
    NAME                                                 DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
    daemonset.apps/monitoring-prometheus-node-exporter   2         2         2       2            2           kubernetes.io/os=linux   105s

    NAME                                                  READY   UP-TO-DATE   AVAILABLE   AGE
    deployment.apps/monitoring-grafana                    1/1     1            1           105s
    deployment.apps/monitoring-kube-prometheus-operator   1/1     1            1           105s
    deployment.apps/monitoring-kube-state-metrics         1/1     1            1           105s

    NAME                                                                    READY   AGE
    statefulset.apps/alertmanager-monitoring-kube-prometheus-alertmanager   1/1     99s
    statefulset.apps/prometheus-monitoring-kube-prometheus-prometheus       1/1     99s
```

What each component does:

| Component | Type | Role |
|---|---|---|
| Prometheus Operator | Deployment | Manages Prometheus and Alertmanager; turns custom resources (e.g. alert rules) into their configuration |
| Prometheus | StatefulSet | Scrapes and stores the metrics |
| Alertmanager | StatefulSet | Receives alerts from Prometheus and sends notifications |
| Grafana | Deployment | Visualizes the metrics in dashboards |
| kube-state-metrics | Deployment | Exposes the state of Kubernetes objects (deployments, pods, etc.) as metrics |
| node-exporter | DaemonSet | Runs on every node and exposes node metrics (CPU, memory, disk) |

To see how Prometheus, Alertmanager and the Operator are configured (containers, config reloaders, mounted config and rule files), their `describe` outputs are saved to files:

```bash
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl describe statefulset prometheus-monitoring-kube-prometheus-prometheus -n monitoring > prom.yaml
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl describe statefulset alertmanager-monitoring-kube-prometheus-alertmanager -n monitoring > alert.yaml
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl describe deployment monitoring-kube-prometheus-operator -n monitoring > operator.yaml
```

</details>

******

<details>
<summary>Data Visualization with Prometheus UI & Grafana</summary>
 <br />


### Demo Executed: Access Prometheus UI and Grafana, Test a CPU Spike

#### Access the UIs with Port-Forward
The Prometheus and Grafana services are `ClusterIP`, so they are only reachable inside the cluster. `kubectl port-forward` opens a tunnel from my machine (`localhost`) through the Kubernetes API server to the service. It runs in the background (`&`) and is only reachable from my own machine.

```bash
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl port-forward service/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 &
    [1] 80067
    Forwarding from 127.0.0.1:9090 -> 9090
    Forwarding from [::1]:9090 -> 9090

    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl port-forward service/monitoring-grafana -n monitoring 8080:80 &
    [2] 84453
    Forwarding from 127.0.0.1:8080 -> 3000
    Forwarding from [::1]:8080 -> 3000
```

#### Prometheus UI
Prometheus UI is at `http://localhost:9090`. **Status > Target health** shows every endpoint Prometheus scrapes (Grafana, Alertmanager, the Operator, kube-state-metrics, node-exporter, kubelet, API server, etc.) and whether the last scrape was successful.

<img width="1909" height="981" alt="image" src="https://github.com/user-attachments/assets/d470023c-a84e-47b0-a382-6c65ff894f5e" />

#### Grafana
Grafana is at `http://localhost:8080`. The user is `admin`; the password is generated by the Helm chart and stored in a Secret:

```bash
    kubectl --namespace monitoring get secrets monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

The chart comes with ready dashboards that use Prometheus as the data source, e.g. **Node Exporter / Nodes** for node CPU, load, memory and disk:

<img width="1912" height="990" alt="image" src="https://github.com/user-attachments/assets/6c9b0e85-c1f7-4784-8672-49794c688016" />

#### Test CPU Spike
To create load on the application, a temporary pod is started inside the cluster and a script sends many requests to the `frontend` service in a loop. `--rm` deletes the pod after exiting the shell.

The image used in the course (`radial/busyboxplus:curl`) is built with an old image manifest format that the containerd version on the current EKS nodes does not support, so `curlimages/curl` is used instead:

```bash
    root@PC:~/modules/prometheus/01-prometheus-stack# kubectl run curl-test --image=curlimages/curl -i --tty --rm -- sh
    If you don't see a command prompt, try pressing enter.
    ~ $ vi test.sh
    ~ $ chmod +x test.sh
    ~ $ ./test.sh
      % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                     Dload  Upload  Total   Spent   Left   Speed
    100  10216   0  10216   0      0 362.0k      0                              0
      % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                     Dload  Upload  Total   Spent   Left   Speed
    100  10216   0  10216   0      0 483.8k      0                              0
    ...
```

The spike is visible in the **Kubernetes / Compute Resources / Cluster** dashboard, in the CPU usage of the `default` namespace:

<img width="1898" height="938" alt="image" src="https://github.com/user-attachments/assets/d3139612-5beb-454b-89e7-430be7d5b733" /> 

</details>

******

<details>
<summary>Create own Alert Rules</summary>
 <br />

### Demo Executed: Alert Rules for High CPU Load and Crash Looping Pods

#### Alert Rules as a Kubernetes Resource
With the Prometheus Operator, alert rules are not written into the Prometheus config file. They are created as a `PrometheusRule` custom resource, and the Operator adds them to Prometheus automatically.

The `release: monitoring` label is required: the Prometheus instance of the Helm chart only loads `PrometheusRule` resources that match its rule selector, which is the Helm release label.

```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: PrometheusRule
    metadata:
      name: main-rules
      namespace: monitoring
      labels:
        app: kube-prometheus-stack
        release: monitoring
    spec:
      groups:
      - name: main.rules
        rules:
        - alert: HostHighCpuLoad
          expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100) > 50
          for: 2m
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            description: " CPU load on host is over 50%\n Value = {{ $value }}\n Instance = {{ $labels.instance }}\n"
            summary: "Host CPU load high"
        - alert: K8sPodCrashLooping
          expr: kube_pod_container_status_restarts_total > 5
          for: 0m
          labels:
            severity: critical
            namespace: monitoring
          annotations:
            description: " Pod: {{ $labels.pod }} is crash looping\n Restarted count: {{ $value }} "
            summary: "k8s pod crash looping"
```

| Field | Meaning |
|---|---|
| `expr` | PromQL condition; the alert is active while it returns a result |
| `for` | How long the condition must stay true before the alert fires |
| `labels` | Extra labels on the alert, used later by Alertmanager for routing (e.g. `severity`) |
| `annotations` | Human-readable text; `{{ $value }}` and `{{ $labels.<name> }}` are filled in with the real values |

**`HostHighCpuLoad`:** `node_cpu_seconds_total{mode="idle"}` is the time each CPU spends idle. `rate(...[2m])` turns it into the idle ratio over the last 2 minutes, `avg by(instance)` averages all CPUs of a node, and `100 - idle%` gives the CPU usage per node. The alert fires when it stays above 50% for 2 minutes.

**`K8sPodCrashLooping`:** fires immediately (`for: 0m`) when a container has restarted more than 5 times.

#### Apply the Rules
```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl apply -f alert-rules.yaml
    prometheusrule.monitoring.coreos.com/main-rules created
    root@PC:~/modules/prometheus/02-alerting# kubectl get PrometheusRule -n monitoring | grep main
    main-rules                                                        43s
```

The Prometheus pod has a `config-reloader` sidecar container. It watches the rule files that the Operator generates and tells Prometheus to reload them:

```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl logs prometheus-monitoring-kube-prometheus-prometheus-0 -n monitoring -c config-reloader
    ...
    level=info ts=2026-10-10T07:48:17.631449771Z caller=reloader.go:546 msg="Reload triggered" cfg_in=/etc/prometheus/config/prometheus.yaml.gz cfg_out=/etc/prometheus/config_out/prometheus.env.yaml cfg_dirs= watched_dirs="/etc/prometheus/rules/prometheus-monitoring-kube-prometheus-prometheus-rulefiles-0, ..."

    root@PC:~/modules/prometheus/02-alerting# kubectl logs prometheus-monitoring-kube-prometheus-prometheus-0 -n monitoring -c prometheus | grep "Completed loading"
    ...
    time=2026-10-10T07:48:17.630Z level=INFO source=main.go:1763 msg="Completed loading of configuration file" ... rules=57.169868ms ... filename=/etc/prometheus/config_out/prometheus.env.yaml totalDuration=66.582448ms
```

The new `main.rules` group is visible in the Prometheus UI under **Alerts**, with both rules in the `inactive` state:

<img width="1909" height="703" alt="image" src="https://github.com/user-attachments/assets/088c579b-12cb-45cd-b0bd-81ee8b461a94" />

#### Test the Alert Rule
A pod that stresses 4 CPUs is started to raise the CPU load on a node:

```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl run cpu-test --image=containerstack/cpustress -- --cpu 4 --timeout 30s --metrics-brief
    pod/cpu-test created
```

An alert goes through three states:

| State | Meaning |
|---|---|
| `inactive` | The condition in `expr` is not true |
| `pending` | The condition is true, but not yet for the `for` duration |
| `firing` | The condition has been true for the `for` duration; the alert is sent to Alertmanager |

When the CPU load goes over 50%, `HostHighCpuLoad` becomes `pending`:

<img width="1902" height="579" alt="image" src="https://github.com/user-attachments/assets/ea379b78-df19-48cc-930d-87560004f601" />

After 2 minutes above 50%, it becomes `firing`:

<img width="1909" height="572" alt="image" src="https://github.com/user-attachments/assets/0bc60db6-cf26-4deb-913c-5c75a00b8c18" />
 
</details>

******

<details>
<summary>Configure Alertmanager with Email Receiver</summary>
 <br />

### Demo Executed: Send Email Notifications for the Alert Rules

#### How Notifications Work
Prometheus only evaluates the alert rules. When an alert is `firing`, Prometheus sends it to **Alertmanager**, which decides where to send it (receivers), how to group it and how often to repeat it (routes).

With the Prometheus Operator, the Alertmanager configuration is added as an `AlertmanagerConfig` custom resource. The Operator merges it into the Alertmanager config and the `config-reloader` sidecar reloads Alertmanager.

#### Email Password as a Secret
The Gmail account has 2-step verification, so the normal account password can't be used for SMTP. A Gmail **App Password** is created for this, and it is stored in a Kubernetes Secret in the same namespace as the `AlertmanagerConfig`:

```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: gmail-auth
      namespace: monitoring
    type: Opaque
    data:
      password: <base64-encoded-app-password>
```

#### AlertmanagerConfig
* **Receiver:** `email` sends notifications through Gmail SMTP; the password is read from the `gmail-auth` Secret.
* **Route:** all alerts go to the `email` receiver and are repeated every 30 minutes while they are still firing. Two child routes match the alerts by name; `K8sPodCrashLooping` is critical, so it is repeated every 10 minutes.
* **Namespace matcher:** the Operator automatically adds a `namespace="monitoring"` matcher to the routes of an `AlertmanagerConfig` in the `monitoring` namespace. This is why the alert rules have the `namespace: monitoring` label; without it, the alerts would not match this config.

```yaml
    apiVersion: monitoring.coreos.com/v1alpha1
    kind: AlertmanagerConfig
    metadata:
      name: main-rules-alert
      namespace: monitoring
    spec:
      route:
        receiver: 'email'
        repeatInterval: 30m
        routes:
        - matchers:
          - name: alertname
            value: HostHighCpuLoad
        - matchers:
          - name: alertname
            value: K8sPodCrashLooping
          repeatInterval: 10m
      receivers:
      - name: 'email'
        emailConfigs:
        - to: 'emrearabacolu@gmail.com'
          from: 'emrearabacolu@gmail.com'
          smarthost: 'smtp.gmail.com:587'
          authUsername: 'emrearabacolu@gmail.com'
          authIdentity: 'emrearabacolu@gmail.com'
          authPassword:
            name: gmail-auth
            key: password
```

#### Apply the Configuration
```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl apply -f email-secret.yaml
    secret/gmail-auth created
    root@PC:~/modules/prometheus/02-alerting# kubectl apply -f alert-manager.yaml
    alertmanagerconfig.monitoring.coreos.com/main-rules-alert created
    root@PC:~/modules/prometheus/02-alerting# kubectl get alertmanagerconfig -n monitoring
    NAME               AGE
    main-rules-alert   37s
```

The `config-reloader` sidecar of the Alertmanager pod reloads the new configuration:

```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl logs alertmanager-monitoring-kube-prometheus-alertmanager-0 -n monitoring -c config-reloader | grep -i "reload triggered"
    ...
    level=info ts=2026-10-10T09:03:42.086257628Z caller=reloader.go:546 msg="Reload triggered" cfg_in=/etc/alertmanager/config/alertmanager.yaml.gz cfg_out=/etc/alertmanager/config_out/alertmanager.env.yaml cfg_dirs= watched_dirs=/etc/alertmanager/config
```

#### Trigger the Alert
The CPU stress pod from the alert rules demo is started again to push the node CPU over 50%:

```bash
    root@PC:~/modules/prometheus/02-alerting# kubectl delete pod cpu-test
    pod "cpu-test" deleted from default namespace
    root@PC:~/modules/prometheus/02-alerting# kubectl run cpu-test --image=containerstack/cpustress -- --cpu 4 --timeout 60s --metrics-brief
    pod/cpu-test created
```

Alertmanager sends the notification email:

<img width="1706" height="1020" alt="image" src="https://github.com/user-attachments/assets/deeb6e9d-60b7-4c96-9824-939faa265bff" />
 
</details>

******


<details>
<summary>Deploy Redis Exporter</summary>
 <br />


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

 
</details>

******

<details>
<summary>Alert Rules & Grafana Dashboard for Redis</summary>
 <br />

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

 
</details>

******

<details>
<summary>Configure& Monitor Own Application with Prometheus Client Library</summary>
 <br />

### Demo Executed: Expose, Scrape and Visualize Metrics of a Node.js App

#### Application Metrics
Third-party apps like Redis need an exporter, but for our own application the metrics can be produced in the code. The Node.js app uses the Prometheus client library for Node.js (`prom-client`): it counts the HTTP requests and measures their duration, and exposes these metrics on the `/metrics` endpoint, in the format Prometheus can scrape.

#### Build and Deploy the App
The image is built from the app's `Dockerfile` (base image updated to `node:20-alpine`, because the current `prom-client` needs a newer Node.js version) and pushed to a private Docker Hub repository (`emrearabacioglu/demo-app:nodeapp`). To pull from the private repository, the cluster needs a `docker-registry` type Secret, which is referenced in the Deployment with `imagePullSecrets`:

```bash
    kubectl create secret docker-registry my-registry-key \
      --docker-server=https://index.docker.io/v1/ \
      --docker-username=emrearabacioglu \
      --docker-password='<password>'
```

#### Kubernetes Configuration
The configuration has three parts:

* **Deployment:** runs the app from the private image; the app listens on port `3000`.
* **Service:** `ClusterIP` service in front of the pods. Its port is named `service`, and the Service itself has the `app: nodeapp` label.
* **ServiceMonitor:** tells Prometheus to scrape the app. It selects the **Service** by its `app: nodeapp` label and scrapes `/metrics` on the port named `service`. The `release: monitoring` label makes the Prometheus instance of the stack pick it up.

```yaml
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nodeapp
      labels:
        app: nodeapp
    spec:
      selector:
        matchLabels:
          app: nodeapp
      template:
        metadata:
          labels:
            app: nodeapp
        spec:
          imagePullSecrets:
          - name: my-registry-key
          containers:
          - name: nodeapp
            image: emrearabacioglu/demo-app:nodeapp
            ports:
            - containerPort: 3000
            imagePullPolicy: Always
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nodeapp
      labels:
        app: nodeapp
    spec:
      type: ClusterIP
      selector:
        app: nodeapp
      ports:
      - name: service
        protocol: TCP
        port: 3000
        targetPort: 3000
    ---
    apiVersion: monitoring.coreos.com/v1
    kind: ServiceMonitor
    metadata:
      name: monitoring-node-app
      labels:
        release: monitoring
        app: nodeapp
    spec:
      endpoints:
      - path: /metrics
        port: service
        targetPort: 3000
      namespaceSelector:
        matchNames:
        - default
      selector:
        matchLabels:
          app: nodeapp
```

How the pieces find each other:

```bash
    Prometheus --(release: monitoring)--> ServiceMonitor --(app: nodeapp)--> Service --(app: nodeapp)--> Pods :3000/metrics
```

```bash
    kubectl apply -f k8s-config.yaml
```

#### Verify the Scrape in Prometheus
The new target `serviceMonitor/default/monitoring-node-app/0` is `UP` under **Status > Target health**:

<img width="1900" height="360" alt="image" src="https://github.com/user-attachments/assets/2fc3a77e-b20b-4d7b-9f23-f71ace5a7d8e" />

The app's metric `http_request_operations_total` (total number of handled requests) can be queried in Prometheus:

<img width="1902" height="367" alt="image" src="https://github.com/user-attachments/assets/aaa29396-5c85-4b7b-90f1-eb07e509a1f2" />

#### Grafana Dashboard
A new dashboard with two panels is created. Counters only grow, so `rate()` is used to turn them into "per second" values over the last 2 minutes:

| Panel | Query |
|---|---|
| Requests per second | `rate(http_request_operations_total[2m])` |
| Requests duration | `rate(http_request_duration_seconds_sum[2m])` |

After sending some requests to the app, the spikes are visible on both panels:

<img width="1919" height="740" alt="image" src="https://github.com/user-attachments/assets/2a69394f-1dcf-46a4-a0f8-a2c2be00a1e0" />

 
</details>

******
