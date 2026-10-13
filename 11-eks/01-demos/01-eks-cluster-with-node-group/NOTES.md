# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create AWS EKS cluster with a Node Group

### Demo Executed: Part 1 – EKS cluster and node group from the AWS console

#### IAM Roles, VPC and Cluster
Created the EKS cluster role, which gives the control plane its permissions:

<img width="1698" height="833" alt="image" src="https://github.com/user-attachments/assets/46aa3448-e58d-4707-be12-49ac1be7bc49" />
<img width="1698" height="529" alt="image" src="https://github.com/user-attachments/assets/dc619f96-ca96-4939-97f1-ab04a9fcd394" />

Created a VPC for the cluster from a CloudFormation template:

<img width="1698" height="589" alt="image" src="https://github.com/user-attachments/assets/b6e1a7fd-774a-4de2-9934-3598d827c965" />

Created the EKS cluster (`eks-cluster-test`):

<img width="1708" height="835" alt="image" src="https://github.com/user-attachments/assets/1c6c455b-96f0-477b-850b-e3c1f9bdc398" />

Created the node group role for the EC2 worker nodes:

<img width="1698" height="667" alt="image" src="https://github.com/user-attachments/assets/c03d8c59-31a6-472b-98b2-4af763e31534" />

Created the node group (EC2 instances that act as worker nodes):

<img width="1700" height="627" alt="image" src="https://github.com/user-attachments/assets/64f0f2a9-ba86-4734-a596-9a14d88618c7" />

#### Local kubeconfig
Checked the AWS CLI config and added the cluster to the local kubeconfig:
```bash
    root@PC:~/k8s-on-aws# aws configure list
    NAME       : VALUE                    : TYPE             : LOCATION
    profile    : <not set>                : None             : None
    access_key : ****************UJWN     : shared-credentials-file :
    secret_key : ****************7sE6     : shared-credentials-file :
    region     : eu-central-1             : config-file      : ~/.aws/config

    root@PC:~/k8s-on-aws# aws eks update-kubeconfig --name eks-cluster-test
    Added new context arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test to /root/.kube/config
```
The kubeconfig now has the EKS cluster next to minikube, and it's the current context:
```bash
    root@PC:~/k8s-on-aws# cat /root/.kube/config
    apiVersion: v1
    clusters:
    - cluster:
        certificate-authority: /root/.minikube/ca.crt
        extensions:
        - extension:
            last-update: Fri, 21 Aug 2026 15:11:57 +03
            provider: minikube.sigs.k8s.io
            version: v1.38.1
          name: cluster_info
        server: https://127.0.0.1:62471
      name: minikube
    - cluster:
        certificate-authority-data: ***
        server: https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com
      name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    contexts:
    - context:
        cluster: minikube
        extensions:
        - extension:
            last-update: Fri, 21 Aug 2026 15:11:57 +03
            provider: minikube.sigs.k8s.io
            version: v1.38.1
          name: context_info
        namespace: default
        user: minikube
      name: minikube
    - context:
        cluster: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
        user: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
      name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    current-context: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
    kind: Config
    users:
    - name: minikube
      user:
        client-certificate: /root/.minikube/profiles/minikube/client.crt
        client-key: /root/.minikube/profiles/minikube/client.key
    - name: arn:aws:eks:eu-central-1:731872836472:cluster/eks-cluster-test
      user:
        exec:
          apiVersion: client.authentication.k8s.io/v1beta1
          args:
          - --region
          - eu-central-1
          - eks
          - get-token
          - --cluster-name
          - eks-cluster-test
          - --output
          - json
          command: aws
```

#### Cluster Access Check
kubectl can reach the cluster. Namespaces, control plane and CoreDNS:
```bash
    root@PC:~/k8s-on-aws# kubectl get namespaces
    NAME               STATUS   AGE
    default            Active   53m
    external-dns       Active   50m
    kube-node-lease    Active   53m
    kube-public        Active   53m
    kube-system        Active   53m

    root@PC:~/k8s-on-aws# kubectl cluster-info
    Kubernetes control plane is running at https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com
    CoreDNS is running at https://7A2D7F94B120CC55857A55F762287E5E.gr7.eu-central-1.eks.amazonaws.com/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

#### Worker Nodes
Both EC2 instances joined the cluster and are `Ready`:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                              STATUS   ROLES    AGE    VERSION
    ip-192-168-223-47.eu-central-1.compute.internal   Ready    <none>   3m8s   v1.36.3-eks-cb19647
    ip-192-168-61-45.eu-central-1.compute.internal    Ready    <none>   3m4s   v1.36.3-eks-cb19647
```

### Demo Executed: Part 2 – Autoscaling

#### IAM Policy for the Autoscaler
The Cluster Autoscaler changes the desired capacity of the node group's Auto Scaling Group, so it needs IAM permissions.

Created a custom IAM policy with the `autoscaling` and `ec2` permissions:

<img width="1700" height="529" alt="image" src="https://github.com/user-attachments/assets/e298cd7d-c3b4-4d05-b945-ea585503b5f7" />
<img width="1682" height="833" alt="image" src="https://github.com/user-attachments/assets/7c28ac5b-58ba-4ccc-8921-5b99094c96ff" />
<img width="1692" height="759" alt="image" src="https://github.com/user-attachments/assets/5591dd32-f5ec-4314-8dbd-0a1ae241b6da" />

Attached the policy to the existing node group role:

<img width="1694" height="809" alt="image" src="https://github.com/user-attachments/assets/17fe26bd-78bc-4f1d-96c8-1f0e3d8d482c" />
<img width="1712" height="607" alt="image" src="https://github.com/user-attachments/assets/90c604a0-4882-4e26-93e9-56bcf45b1db9" />
<img width="1700" height="695" alt="image" src="https://github.com/user-attachments/assets/ee1f0128-b909-40ba-b6fb-b8e7e182af6d" />

#### Cluster Autoscaler Deployment
Applied `cluster-autoscaler-autodiscover.yaml`. The first apply failed on the ServiceAccount annotation (YAML error). After fixing it, the second apply created the ServiceAccount and the autoscaler pod started:
```bash
    root@PC:~/k8s-on-aws# cat cluster-autoscaler-autodiscover.yaml
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      labels:
        k8s-addon: cluster-autoscaler.addons.k8s.io
        k8s-app: cluster-autoscaler
      name: cluster-autoscaler
      namespace: kube-system
      annotations:
        eks.amazonaws.com/role-arn:arn:aws:iam::731872836472:role/EKSServiceAccountRole
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: cluster-autoscaler
      labels:
        k8s-addon: cluster-autoscaler.addons.k8s.io
        k8s-app: cluster-autoscaler
    rules:
      - apiGroups: [""]
        resources: ["events", "endpoints"]
        verbs: ["create", "patch"]
    ... [Truncated for brevity] ...
    
    root@PC:~/k8s-on-aws# kubectl apply -f cluster-autoscaler-autodiscover.yaml
    clusterrole.rbac.authorization.k8s.io/cluster-autoscaler created
    ...
    error: unable to decode "cluster-autoscaler-autodiscover.yaml": json: cannot unmarshal string into Go struct field ObjectMeta.metadata.annotations of type map[string]string
    
    root@PC:~/k8s-on-aws# kubectl apply -f cluster-autoscaler-autodiscover.yaml
    serviceaccount/cluster-autoscaler created
    clusterrole.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    role.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    clusterrolebinding.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    rolebinding.rbac.authorization.k8s.io/cluster-autoscaler unchanged
    deployment.apps/cluster-autoscaler unchanged
    
    root@PC:~/k8s-on-aws# kubectl get pod -n kube-system
    NAME                                 READY   STATUS    RESTARTS   AGE
    aws-node-7qbqs                       2/2     Running   0          173m
    cluster-autoscaler-fb4856648-qj8xr   1/1     Running   0          57s
    coredns-c4b9957df-k7n97              1/1     Running   0          16h
```

#### Nginx with a LoadBalancer Service
Deployed nginx with a `type: LoadBalancer` service. AWS created a load balancer and its DNS name is the `EXTERNAL-IP`:
```bash
    root@PC:~/k8s-on-aws# cat nginx-config.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
    spec:
      selector:
        matchLabels:
          app: nginx
      replicas: 1
      template:
        metadata:
          labels:
            app: nginx
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
      
    root@PC:~/k8s-on-aws# kubectl apply -f nginx-config.yaml
    deployment.apps/nginx created
    service/nginx created
    
    root@PC:~/k8s-on-aws# kubectl get svc
    NAME         TYPE           CLUSTER-IP       EXTERNAL-IP                                                               PORT(S)        AGE
    kubernetes   ClusterIP      10.100.0.1       <none>                                                                    443/TCP        19h
    nginx        LoadBalancer   10.100.190.149   a4d6933ade5dd4ec39879d432e7de9d9-1736632215.eu-central-1.elb.amazonaws.com   80:30823/TCP   27s
```
<img width="1700" height="825" alt="image" src="https://github.com/user-attachments/assets/96cee4d3-9f84-416e-84a9-443603ec2e07" />
<img width="1706" height="403" alt="image" src="https://github.com/user-attachments/assets/d5d499af-7cc2-41eb-9ec1-fd470b88a2d5" />

#### Scaling Up and Down
Changed the nginx deployment to 20 replicas. The new pods were `Pending` because the node didn't have enough resources:
```bash
    root@PC:~/k8s-on-aws# kubectl edit deployment nginx
    deployment.apps/nginx edited
    
    root@PC:~/k8s-on-aws# kubectl get pod
    NAME                     READY   STATUS    RESTARTS   AGE
    nginx-5cf8dc6bc5-277m6   0/1     Pending   0          9s
    nginx-5cf8dc6bc5-2h9bn   0/1     Pending   0          9s
    nginx-5cf8dc6bc5-2wtmp   1/1     Running   0          21m
    nginx-5cf8dc6bc5-56zbl   0/1     Pending   0          9s
    ...
```
Cluster Autoscaler logs: it saw the unschedulable pods and set the node group size from 1 to 3:
```bash
    I0902 12:04:23.513273        1 static_autoscaler.go:569] Unschedulable pods are very new, waiting one iteration for more
    I0902 12:04:34.098520        1 orchestrator.go:120] Upcoming 2 nodes
    I0902 12:04:33.899713        1 executor.go:166] Scale-up: setting group eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 size to 3
    I0902 12:04:34.087353        1 event_sink_logging_wrapper.go:48] Event(v1.ObjectReference{Kind:"Pod", Namespace:"default", Name:"nginx-5cf8dc6bc5-k9k52" ... reason: 'TriggeredScaleUp' pod triggered scale-up: [{eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 1->3 (max: 3)}]
```
The two new nodes joined and are `Ready`:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                               STATUS   ROLES    AGE     VERSION
    ip-192-168-195-122.eu-central-1.compute.internal   Ready    <none>   2m26s   v1.36.3-eks-cb19647
    ip-192-168-208-204.eu-central-1.compute.internal   Ready    <none>   2m22s   v1.36.3-eks-cb19647
    ip-192-168-51-213.eu-central-1.compute.internal    Ready    <none>   3h46m   v1.36.3-eks-cb19647
```
After scaling the deployment back down, the extra nodes were cordoned (`SchedulingDisabled`) and then removed:
```bash
    root@PC:~/k8s-on-aws# kubectl get node
    NAME                                               STATUS                     ROLES    AGE   VERSION
    ip-192-168-195-122.eu-central-1.compute.internal   Ready,SchedulingDisabled   <none>   15m   v1.36.3-eks-cb19647
    ip-192-168-208-204.eu-central-1.compute.internal   Ready,SchedulingDisabled   <none>   15m   v1.36.3-eks-cb19647
    ip-192-168-51-213.eu-central-1.compute.internal    Ready                      <none>   4h    v1.36.3-eks-cb19647
    
    root@PC:~/k8s-on-aws# kubectl get node
    NAME                                              STATUS   ROLES    AGE    VERSION
    ip-192-168-51-213.eu-central-1.compute.internal   Ready    <none>   4h1m   v1.36.3-eks-cb19647
```
