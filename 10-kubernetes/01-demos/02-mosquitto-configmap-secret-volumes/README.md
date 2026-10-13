# Deploy Mosquitto message broker with ConfigMap and Secret Volume Types

**Technologies:** Kubernetes, Docker, Mosquitto

I gave the Mosquitto message broker its configuration file and a secret file by mounting a ConfigMap and a Secret as volumes, not as environment variables.

## Summary
- First ran Mosquitto with `mosquitto-without-volumes.yaml` and looked at the default `mosquitto.conf` inside the container, then deleted it.
- `config-file.yaml` is a ConfigMap with my own `mosquitto.conf` (logging settings and `listener 9001`).
- `secret-file.yaml` is a Secret that holds a file called `secret.file`.
- `mosquitto.yaml` is the Mosquitto Deployment that mounts the ConfigMap to `/mosquitto/config` and the Secret to `/mosquitto/secret` (read-only).
- Checked inside the pod: `mosquitto.conf` is the one from the ConfigMap and `secret.file` is there already decoded.

## Run
```bash
kubectl apply -f config-file.yaml
kubectl apply -f secret-file.yaml
kubectl apply -f mosquitto.yaml
kubectl exec -it <pod> -- /bin/sh
```

## Result
The new pod is running and the config file inside it comes from the ConfigMap:
```
root@PC:~# kubectl get pod
NAME                                 READY   STATUS    RESTARTS       AGE
...
mosquitto-cf9f594cd-dr9wz            1/1     Running   0              12s
...
/mosquitto/config # cat mosquitto.conf
log_dest stdout
log_type all
log_timestamp true
listener 9001
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
