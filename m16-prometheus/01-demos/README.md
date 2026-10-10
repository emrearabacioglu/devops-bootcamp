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

 content will be here

 
</details>

******

<details>
<summary>Trigger Alerts for Email Receiver</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Deploy Redis Exporter</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Alert Rules & Grafana Dashboard for Redis</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Collect & Expose Metrics with Prometheus Client Library (Monitor own App - Part 1)</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Scrape Own Application Metrics & Configure Own Grafana Dashboard (Monitor own App - Part 2)</summary>
 <br />

 content will be here

 
</details>

******
