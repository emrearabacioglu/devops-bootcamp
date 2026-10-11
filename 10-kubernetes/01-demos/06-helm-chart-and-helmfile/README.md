# Create Helm Chart for Microservices / Deploy Microservices with Helmfile

**Technologies:** Kubernetes, Helm, Helmfile

The online shop services all need almost the same Deployment and Service, so I made one shared Helm chart for them and a separate chart for Redis. Then I deployed all of them first with a `helm install` script and then with Helmfile (on Minikube).

## Summary
1. Created the shared chart `charts/microservice/` with `helm create`. `templates/deployment.yaml` and `templates/service.yaml` take the name, replicas, image, version, ports, env vars and service type from the values.
2. Wrote one values file per service in `values/` (e.g. `values/email-service-values.yaml`). Tested the chart by installing emailservice and recommendationservice with their own values files.
3. Redis got its own chart, `charts/redis/`, with TCP probes, resource limits and an `emptyDir` volume. Checked it with `helm template` and `helm install --dry-run` using `values/redis-values.yaml`.
4. `install.sh` runs one `helm install` per service (11 releases) and `uninstall.sh` removes them. Ran both.
5. Installed Helmfile 0.164.0 and wrote `helmfile.yaml`, which lists every release with its chart and values file. For `rediscart` it overrides `appReplicas` and `volumeName` inline.
6. Deployed everything with `helmfile sync`, checked with `helmfile list` and `kubectl get pod`, and removed it with `helmfile destroy`.

## Run
```bash
# with Helm only
chmod u+x install.sh
./install.sh
./uninstall.sh

# with Helmfile
helmfile sync
helmfile list
helmfile destroy
```

## Result
`helmfile sync` installed the releases from both charts and the pods are running:
```
root@PC:~/k8s/microservices# helmfile list
NAME                    NAMESPACE       ENABLED INSTALLED       LABELS  CHART                   VERSION
rediscart                               true    true                    charts/redis
emailservice                            true    true                    charts/microservice
...

root@PC:~/k8s/microservices# kubectl get pod
NAME                                     READY   STATUS    RESTARTS   AGE
adservice-5f8b8889c9-jzgmv               1/1     Running   0          46s
cartservice-548cc667f7-8tfrw             1/1     Running   0          47s
...
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
