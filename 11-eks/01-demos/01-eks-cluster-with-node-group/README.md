# Create AWS EKS cluster with a Node Group

**Technologies:** Kubernetes, AWS EKS

I created an EKS cluster with an EC2 node group in the AWS console, added the Cluster Autoscaler and deployed nginx to test scaling.

## Summary
1. Created two IAM roles in the AWS console: one for the EKS cluster (control plane) and one for the worker nodes.
2. Created the VPC from a CloudFormation template and created the EKS cluster `eks-cluster-test` in it.
3. Created a node group (EC2 worker nodes) and attached it to the cluster. Connected my local `kubectl` with `aws eks update-kubeconfig`.
4. Created an IAM policy with `autoscaling` and `ec2` permissions and attached it to the node group role.
5. Deployed the Cluster Autoscaler with `cluster-autoscaler-autodiscover.yaml`, edited with my cluster name and the IAM role annotation on the ServiceAccount. The first apply failed on a YAML error in that annotation; after fixing it the autoscaler pod started.
6. Deployed nginx with a LoadBalancer Service (`nginx-config.yaml`). AWS created a load balancer for it.
7. Set nginx to 20 replicas. The new pods were `Pending`, and the autoscaler scaled the node group from 1 to 3 nodes. After scaling back down, the extra nodes were removed.

## Run
```bash
aws eks update-kubeconfig --name eks-cluster-test
kubectl apply -f cluster-autoscaler-autodiscover.yaml
kubectl apply -f nginx-config.yaml
kubectl edit deployment nginx
kubectl get nodes
```

## Result
The autoscaler pod is running, it scales the node group up to 3, and the new nodes join the cluster:
```
root@PC:~/k8s-on-aws# kubectl get pod -n kube-system
NAME                                 READY   STATUS    RESTARTS   AGE
...
cluster-autoscaler-fb4856648-qj8xr   1/1     Running   0          57s
...
I0902 12:04:33.899713        1 executor.go:166] Scale-up: setting group eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 size to 3
...
root@PC:~/k8s-on-aws# kubectl get nodes
NAME                                               STATUS   ROLES    AGE     VERSION
ip-192-168-195-122.eu-central-1.compute.internal   Ready    <none>   2m26s   v1.36.3-eks-cb19647
ip-192-168-208-204.eu-central-1.compute.internal   Ready    <none>   2m22s   v1.36.3-eks-cb19647
ip-192-168-51-213.eu-central-1.compute.internal    Ready    <none>   3h46m   v1.36.3-eks-cb19647
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
