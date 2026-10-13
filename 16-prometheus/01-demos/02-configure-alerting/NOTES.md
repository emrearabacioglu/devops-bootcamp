# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Configure Alerting for our Application

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
