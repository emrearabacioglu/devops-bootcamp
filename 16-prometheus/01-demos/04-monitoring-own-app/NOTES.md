# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Configure Monitoring for Own Application

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
