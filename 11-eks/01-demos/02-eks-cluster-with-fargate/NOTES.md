# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create EKS cluster with Fargate profile

### Demo Executed: Run nginx pods on Fargate

#### Pod Execution Role and Fargate Profile
Created an EKS pod execution role. Fargate uses it to pull images and run the pods:

<img width="1692" height="821" alt="image" src="https://github.com/user-attachments/assets/2c5a62b3-6016-4b60-b461-0c6c15329371" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/d1fa5fd5-bbb3-4f78-996b-9f05966eee81" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/9c97736e-5c02-4c43-983c-7a0834ccfff0" />

Created a Fargate profile for the `dev` namespace with the selector `profile: fargate`. Pods that match it run on Fargate instead of the EC2 node group:

<img width="1694" height="801" alt="image" src="https://github.com/user-attachments/assets/38ddab5a-aeb3-4bc5-8afc-428a04e9ebfd" />
<img width="1708" height="689" alt="image" src="https://github.com/user-attachments/assets/720afcfd-4bd0-47df-b8e2-e709c85882d6" />
<img width="1706" height="601" alt="image" src="https://github.com/user-attachments/assets/f5ad4eee-d27e-4bd2-93a2-eeab50e0c77e" />
<img width="1690" height="799" alt="image" src="https://github.com/user-attachments/assets/8e65ff03-f43f-4dbb-b6b7-61c7573798ea" />

#### Deploying to Fargate
The nginx manifest uses namespace `dev` and the `profile: fargate` label to match the profile:
```bash
    root@PC:~/k8s-on-aws# cat nginx-config.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
      namespace: dev
      labels:
        app: nginx
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: nginx
          profile: fargate
    template:
      metadata:
        labels:
          app: nginx
          profile: fargate
      spec:
        containers:
        - name: nginx
          image: nginx
          ports:
          - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      ports:
      - name: http
        port: 80
        protocol: TCP
        targetPort: 80
      selector:
        app: nginx
      type: LoadBalancer
```
Created the `dev` namespace and applied the manifest:
```bash
    root@PC:~/k8s-on-aws# kubectl get ns
    NAME              STATUS   AGE
    default           Active   21h
    external-dns      Active   21h
    kube-node-lease   Active   21h
    kube-public       Active   21h
    kube-system       Active   21h
    
    root@PC:~/k8s-on-aws# kubectl create ns dev
    namespace/dev created
    
    root@PC:~/k8s-on-aws# kubectl apply -f nginx-config.yaml
    deployment.apps/nginx created
    service/nginx unchanged
```
Watched the pods. They stayed `Pending` for about a minute while Fargate started the compute for them, then went to `Running`:
```bash
    root@PC:~/k8s-on-aws# kubectl get pods -n dev -w
    NAME                    READY   STATUS    RESTARTS   AGE
    nginx-fd684dfd4-p8jpq   0/1     Pending   0          33s
    nginx-fd684dfd4-vs9zt   0/1     Pending   0          33s
    nginx-fd684dfd4-vs9zt   0/1     Pending   0          51s
    nginx-fd684dfd4-vs9zt   0/1     ContainerCreating   0          52s
    nginx-fd684dfd4-vs9zt   0/1     ContainerCreating   0          52s
    nginx-fd684dfd4-vs9zt   1/1     Running             0          58s
    nginx-fd684dfd4-p8jpq   0/1     Pending             0          59s
    nginx-fd684dfd4-p8jpq   0/1     ContainerCreating   0          59s
    nginx-fd684dfd4-p8jpq   0/1     ContainerCreating   0          60s
    nginx-fd684dfd4-p8jpq   1/1     Running             0          66s
```
Two Fargate nodes appeared next to the existing EC2 node:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                                      STATUS   ROLES    AGE     VERSION
    fargate-ip-192-168-152-97.eu-central-1.compute.internal   Ready    <none>   6m48s   v1.36.2-eks-254016e
    fargate-ip-192-168-165-70.eu-central-1.compute.internal   Ready    <none>   6m56s   v1.36.2-eks-254016e
    ip-192-168-51-213.eu-central-1.compute.internal           Ready    <none>   5h47m   v1.36.3-eks-cb19647
```
