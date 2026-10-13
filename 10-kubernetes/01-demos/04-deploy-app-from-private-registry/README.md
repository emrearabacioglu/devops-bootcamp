# Deploy our web application in K8s cluster from private Docker registry

**Technologies:** Kubernetes, Helm, AWS ECR, Docker

I pushed the Node.js demo app image to a private AWS ECR repository and deployed it on Minikube. To pull the image, Kubernetes needs the registry credentials in a Secret.

## Summary
- Created the `js-app` repository in ECR (`eu-central-1`), built the image, tagged it as `731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2` and pushed it.
- Logged in to ECR inside the Minikube node and copied its `.docker/config.json` to the host.
- Tried different ways to create the registry Secret:
  - `docker-secret.yaml`: Secret of type `kubernetes.io/dockerconfigjson` with the base64 `config.json` (value replaced with `***`)
  - `kubectl create secret generic my-registry-key --from-file=...` from the same `config.json`
  - `kubectl create secret docker-registry my-registry-key-two` with the server, username and password given directly
- The first Deployment without credentials ended in `ImagePullBackOff`.
- Added `imagePullSecrets` with `my-registry-key-two` to `my-app-deployment.yaml`. After that the image was pulled and the pod started.

## Run
```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 731872836472.dkr.ecr.eu-central-1.amazonaws.com
docker push 731872836472.dkr.ecr.eu-central-1.amazonaws.com/js-app:1.2

kubectl create secret docker-registry my-registry-key-two \
    --docker-server=https://731872836472.dkr.ecr.eu-central-1.amazonaws.com \
    --docker-username=AWS \
    --docker-password=***
kubectl apply -f my-app-deployment.yaml
```

## Result
Without the Secret the pod can't pull the image. With `imagePullSecrets` it runs:
```
root@PC:~# kubectl get pod
NAME                     READY   STATUS             RESTARTS   AGE
my-app-568ff5465-728m8   0/1     ImagePullBackOff   0          4s
...
root@PC:~# kubectl apply -f my-app-deployment.yaml
deployment.apps/my-app-two created

root@PC:~# kubectl get pod
NAME                          READY   STATUS    RESTARTS   AGE
my-app-two-5bdb94fbc4-lwc6n   1/1     Running   0          6s
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
