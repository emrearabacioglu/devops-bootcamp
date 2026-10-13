# Create EKS cluster with Fargate profile

**Technologies:** Kubernetes, AWS EKS, AWS Fargate

I added a Fargate profile to my EKS cluster and deployed nginx pods that run on Fargate instead of the EC2 node group.

## Summary
1. Created an EKS pod execution role in IAM. Fargate uses it to pull images and run the pods.
2. Created a Fargate profile for namespace `dev` with the selector `profile: fargate`. Pods that match it run on Fargate.
3. `nginx-config.yaml` has an nginx Deployment (2 replicas) in namespace `dev` with the labels `app: nginx` and `profile: fargate`, and a LoadBalancer Service.
4. Created the `dev` namespace and applied the file. The pods stayed `Pending` for about a minute while Fargate started the compute, then went to `Running`.
5. Each Fargate pod got its own node, next to the existing EC2 node.

## Run
```bash
kubectl create ns dev
kubectl apply -f nginx-config.yaml
kubectl get pods -n dev -w
kubectl get nodes
```

## Result
Both nginx pods are running and two Fargate nodes appear next to the EC2 node:
```
root@PC:~/k8s-on-aws# kubectl get pods -n dev -w
...
nginx-fd684dfd4-vs9zt   1/1     Running             0          58s
...
nginx-fd684dfd4-p8jpq   1/1     Running             0          66s

root@PC:~/k8s-on-aws# kubectl get nodes
NAME                                                      STATUS   ROLES    AGE     VERSION
fargate-ip-192-168-152-97.eu-central-1.compute.internal   Ready    <none>   6m48s   v1.36.2-eks-254016e
fargate-ip-192-168-165-70.eu-central-1.compute.internal   Ready    <none>   6m56s   v1.36.2-eks-254016e
ip-192-168-51-213.eu-central-1.compute.internal           Ready    <none>   5h47m   v1.36.3-eks-cb19647
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
