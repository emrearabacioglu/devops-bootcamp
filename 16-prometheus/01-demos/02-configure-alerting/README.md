# Configure Alerting for our Application

**Technologies:** Prometheus, Kubernetes, Linux

I added two alert rules to Prometheus (CPU usage over 50% and a crash looping pod) and configured Alertmanager to send an email when they fire.

## Summary
1. Wrote `alert-rules.yaml`, a `PrometheusRule` resource with the `main.rules` group:
   - `HostHighCpuLoad`: CPU usage of a node is over 50% for 2 minutes.
   - `K8sPodCrashLooping`: a container has restarted more than 5 times.

   The `release: monitoring` label is needed so the Prometheus of the Helm chart loads the rules.
2. Applied it and checked in the `config-reloader` logs that Prometheus reloaded the rules.
3. Started a CPU stress pod (`containerstack/cpustress`) and watched `HostHighCpuLoad` go from `inactive` to `pending` to `firing` in the Prometheus UI.
4. Created a Gmail App Password and stored it in the `gmail-auth` Secret (`email-secret.yaml`). The password in this file is masked (`***`).
5. Wrote `alert-manager.yaml`, an `AlertmanagerConfig` with an `email` receiver (Gmail SMTP) and a route for each alert. `K8sPodCrashLooping` repeats every 10 minutes, the rest every 30 minutes.
6. Applied both files, started the CPU stress pod again and got the alert email from Alertmanager.

`config-microservices.yaml` is the same Online Boutique app as in `01-install-prometheus-stack`.

## Run
```bash
kubectl apply -f alert-rules.yaml
kubectl apply -f email-secret.yaml
kubectl apply -f alert-manager.yaml
kubectl run cpu-test --image=containerstack/cpustress -- --cpu 4 --timeout 60s --metrics-brief
```

## Result
The rules, the Secret and the Alertmanager config are created. The firing alert and the received email were checked in the Prometheus UI and Gmail.
```
root@PC:~/modules/prometheus/02-alerting# kubectl apply -f alert-rules.yaml
prometheusrule.monitoring.coreos.com/main-rules created
...
root@PC:~/modules/prometheus/02-alerting# kubectl apply -f email-secret.yaml
secret/gmail-auth created
root@PC:~/modules/prometheus/02-alerting# kubectl apply -f alert-manager.yaml
alertmanagerconfig.monitoring.coreos.com/main-rules-alert created
root@PC:~/modules/prometheus/02-alerting# kubectl get alertmanagerconfig -n monitoring
NAME               AGE
main-rules-alert   37s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
