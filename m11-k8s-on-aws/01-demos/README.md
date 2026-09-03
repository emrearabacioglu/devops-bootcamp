******

<details>

<summary>Create EKS cluster with Node Group - Part 1</summary>
 <br />
 
### EKS Cluster Infrastructure and Configuration

#### AWS IAM, VPC, and EKS Cluster Provisioning
Configured the foundational AWS infrastructure required for the Kubernetes environment. 
*   Created the EKS Cluster Role to grant Kubernetes control plane permissions.
*   <img width="1698" height="833" alt="image" src="https://github.com/user-attachments/assets/46aa3448-e58d-4707-be12-49ac1be7bc49" />
*   <img width="1698" height="529" alt="image" src="https://github.com/user-attachments/assets/dc619f96-ca96-4939-97f1-ab04a9fcd394" />

*   Provisioned a dedicated VPC utilizing a CloudFormation template.
*   <img width="1698" height="589" alt="image" src="https://github.com/user-attachments/assets/b6e1a7fd-774a-4de2-9934-3598d827c965" />

*   Deployed the EKS cluster (`eks-cluster-test`).
*   <img width="1708" height="835" alt="image" src="https://github.com/user-attachments/assets/1c6c455b-96f0-477b-850b-e3c1f9bdc398" />


*   Created the Node Group Role to authorize EC2 worker nodes.
*   <img width="1698" height="667" alt="image" src="https://github.com/user-attachments/assets/c03d8c59-31a6-472b-98b2-4af763e31534" />

*   Provisioned the Node Group (EC2 Instances) to act as the cluster's worker nodes.
*   <img width="1700" height="627" alt="image" src="https://github.com/user-attachments/assets/64f0f2a9-ba86-4734-a596-9a14d88618c7" />


#### Local Environment Configuration
Verified the local AWS CLI profile configuration and successfully fetched the EKS cluster configuration to update the local `kubeconfig` file.
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
Demonstrated the successful generation of the local Kubernetes configuration file:
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
        certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUREakNDQWZhZ0F3SUJBZ0lSQUtWME9SZXhzSmRmOUVkV01Cc2lJMTB3RFFZSktvWklodmNOQVFFTEJRQXcKRlRFVE1CRUdBMVVFQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TmpBNU1ERXhOakU0TWpOYUZ3MHpNVEE0TXpFeApOakU0TWpOYU1CVXhFekFSQmdOVkJBTVRDbXQxWW1WeWJtVjBaWE13Z2dFaU1BMEdDU3FHU0liM0RRRUJBUVVBCkE0SUJEd0F3Z2dFS0FvSUJBUURONC9zbStuVENoNkE3L2N1ZExuTTJySXBoWWdsb3krYkUyVzRoVE9OYlZoejAKeUM1VStNOC9EWDFvb3pFdXRrRUlrOFM0YUNrakZSMUl0S1E1L3RuM0dlTnc0TkN5T1ZScUgxcldzR1B1V2VZSgppT0VxK0NPeHE5a24wY0VjaVgxU0ZzQWtLbjNqQUg2RWJZc2lDR0pHTUltRkZabGVVTlZZN01GU21WNWpoYmo3CmhKRXZocE1ya0NnZ2I4VlRpNlFGVm5NeXVFdTI2RGp2K2h3SHdNd0V0M1ZhQUsxUjhGcmswSDc1MVdBeGtHaFAKQU9vR0xxVTlRNllyYi9VbDQ3eUhsT3diclVOU2h1YzhzNFBURlZmcUhUWlVYVzhxUCs0b1ZaN3R3WlBpOFZKaApnS2UxeGVXbDZJMFhvNVowcGtKSWxBODlZcjZqVXFsZHU0QXlvdnFMQWdNQkFBR2pXVEJYTUE0R0ExVWREd0VCCi93UUVBd0lDcERBUEJnTlZIUk1CQWY4RUJUQURBUUgvTUIwR0ExVWREZ1FXQkJRdmYzM1Qzc1I3SDFWQVlFZlgKQkV2MWFJZVIwekFWQmdOVkhSRUVEakFNZ2dwcmRXSmxjbTVsZEdWek1BMEdDU3FHU0liM0RRRUJDd1VBQTRJQgpBUUNPc1A3UEoySjZ6NHY3SEduZVZlYk5TeGlVZUw4NjdHRDJoK3ZsdUhhODV3WVVoa2ZXQU5hVWcvcSt6Z2drCjFEV3B4L3BlV2thalJDUUZoclVtSTVneTlOV1Fxd2hqNDVZOXp2SHVNM01scVpIQW9FYVY4WHFRQzZRYmlpRDEKaFNtRHRFY2h5cVIycVpmU21zVGw1S0VDTmoyUFBvUlhnRFV5d0g0Ti90Y3cxWTloL2pCekRBV0dCRUlHNy90aQpzQUs5TmN1WXBaRngvTW5VbUxzUkVtOUIxNFIrejN1dUZEMHhZdm0yaEdJRytTd1Jnd0E5cVVUNC9qc1VqQWlnCktOQ2tZTlhBU2VFNjBrNXljNERFc1N4d2RyZG1SVS9hZUhhTzVVSzFncjVqdTNGQk4xb3JEN29Tc0EyZlluMCsKdmtCS0k3eXpPVHpjN3p6WTFrS3BUMGltCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
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
#### IAM Authentication Resolution & Cluster Verification


Successfully validated cluster connectivity, retrieved namespaces, and verified the control plane and CoreDNS operation.
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
#### Worker Node Initialization
Verified that the provisioned EC2 instances successfully joined the EKS cluster and reported a `Ready` status, preparing the environment for workload scheduling.
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                              STATUS   ROLES    AGE    VERSION
    ip-192-168-223-47.eu-central-1.compute.internal   Ready    <none>   3m8s   v1.36.3-eks-cb19647
    ip-192-168-61-45.eu-central-1.compute.internal    Ready    <none>   3m4s   v1.36.3-eks-cb19647
```

 
</details>

******

<details>

<summary>Create EKS cluster with Node Group - Part 2 (Autoscaling)</summary>
 <br />
 
### EKS Auto-Scaling and Application Deployment

#### AWS IAM and Auto-Scaling Policy Configuration
Configured AWS Identity and Access Management (IAM) to authorize the Kubernetes Cluster Autoscaler to dynamically modify the Desired Capacity of the underlying Auto Scaling Group. 
*   Created a custom IAM Policy with required `autoscaling` and `ec2` permissions.
  <img width="1700" height="529" alt="image" src="https://github.com/user-attachments/assets/e298cd7d-c3b4-4d05-b945-ea585503b5f7" />
  <img width="1682" height="833" alt="image" src="https://github.com/user-attachments/assets/7c28ac5b-58ba-4ccc-8921-5b99094c96ff" />
  <img width="1692" height="759" alt="image" src="https://github.com/user-attachments/assets/5591dd32-f5ec-4314-8dbd-0a1ae241b6da" />

*   Attached the new policy to the existing EKS Node Group Role.

  <img width="1694" height="809" alt="image" src="https://github.com/user-attachments/assets/17fe26bd-78bc-4f1d-96c8-1f0e3d8d482c" />
  <img width="1712" height="607" alt="image" src="https://github.com/user-attachments/assets/90c604a0-4882-4e26-93e9-56bcf45b1db9" />
  <img width="1700" height="695" alt="image" src="https://github.com/user-attachments/assets/ee1f0128-b909-40ba-b6fb-b8e7e182af6d" />


#### Cluster Autoscaler Deployment
Prepared and deployed the Cluster Autoscaler component. Addressed a YAML syntax error in the annotations map, reapplied the manifest, and verified the pod's operational status.
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
#### Nginx Application & Service Provisioning
Deployed an Nginx sample application and exposed it externally utilizing a Kubernetes `type: LoadBalancer` Service, seamlessly provisioning an AWS Classic/Network Load Balancer.
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


#### Cluster Auto-Scaling Demonstration
Demonstrated infrastructure elasticity by scaling the Nginx deployment up to 20 replicas. The Autoscaler accurately detected unschedulable pods due to resource exhaustion and dynamically expanded the Node Group capacity. Subsequent manual scale-down triggered safe node evictions (`SchedulingDisabled`) and termination.
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
Verified the Cluster Autoscaler logs acknowledging the deficit and triggering scale-up routines:
```bash
    I0902 12:04:23.513273        1 static_autoscaler.go:569] Unschedulable pods are very new, waiting one iteration for more
    I0902 12:04:34.098520        1 orchestrator.go:120] Upcoming 2 nodes
    I0902 12:04:33.899713        1 executor.go:166] Scale-up: setting group eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 size to 3
    I0902 12:04:34.087353        1 event_sink_logging_wrapper.go:48] Event(v1.ObjectReference{Kind:"Pod", Namespace:"default", Name:"nginx-5cf8dc6bc5-k9k52" ... reason: 'TriggeredScaleUp' pod triggered scale-up: [{eks-eks-node-group-bad02f24-c810-afdf-2bab-6e88222abb34 1->3 (max: 3)}]
```
Validated the successful initialization and registration of new EC2 Worker Nodes:
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                               STATUS   ROLES    AGE     VERSION
    ip-192-168-195-122.eu-central-1.compute.internal   Ready    <none>   2m26s   v1.36.3-eks-cb19647
    ip-192-168-208-204.eu-central-1.compute.internal   Ready    <none>   2m22s   v1.36.3-eks-cb19647
    ip-192-168-51-213.eu-central-1.compute.internal    Ready    <none>   3h46m   v1.36.3-eks-cb19647
```
Initiated deployment scale-down and validated the Cordon/Drain operations as nodes transitioned to `SchedulingDisabled` prior to permanent termination:
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

 
</details>


******

<details>
<summary>Create EKS cluster with Fargate</summary>
 <br />
 
 ### AWS EKS with Fargate Integration

#### Fargate IAM Role and Profile Provisioning
Configured the serverless compute engine for the EKS cluster by provisioning AWS Fargate. 
*   Created a dedicated Amazon EKS Pod Execution Role to grant Fargate infrastructure the required permissions to pull container images and execute pods securely.
<img width="1692" height="821" alt="image" src="https://github.com/user-attachments/assets/2c5a62b3-6016-4b60-b461-0c6c15329371" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/d1fa5fd5-bbb3-4f78-996b-9f05966eee81" />
<img width="1674" height="813" alt="image" src="https://github.com/user-attachments/assets/9c97736e-5c02-4c43-983c-7a0834ccfff0" />

  
*   Established a Fargate Profile bound to the `dev` namespace, utilizing the `profile: fargate` selector to automatically route matching workloads to serverless nodes instead of the standard EC2 Node Group.
<img width="1694" height="801" alt="image" src="https://github.com/user-attachments/assets/38ddab5a-aeb3-4bc5-8afc-428a04e9ebfd" />
<img width="1708" height="689" alt="image" src="https://github.com/user-attachments/assets/720afcfd-4bd0-47df-b8e2-e709c85882d6" />
<img width="1706" height="601" alt="image" src="https://github.com/user-attachments/assets/f5ad4eee-d27e-4bd2-93a2-eeab50e0c77e" />
<img width="1690" height="799" alt="image" src="https://github.com/user-attachments/assets/8e65ff03-f43f-4dbb-b6b7-61c7573798ea" />



#### Application Deployment via AWS Fargate
Demonstrated serverless pod execution by deploying an Nginx application explicitly targeted at the newly created Fargate profile. Verified the manifest configuration specifying the exact namespace and matching labels.
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
Prepared the cluster environment by establishing the designated logical partition (`dev`) and executing the deployment.
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
Monitored the Fargate dynamic provisioning process in real-time. The pods initially entered a `Pending` state while AWS spun up isolated serverless compute environments on-demand, successfully transitioning to `Running` once the backend nodes initialized.
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
Validated the cluster's underlying infrastructure scaling to confirm the injection of the dynamic Fargate nodes, operating seamlessly alongside the pre-existing EC2 worker node.
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                                      STATUS   ROLES    AGE     VERSION
    fargate-ip-192-168-152-97.eu-central-1.compute.internal   Ready    <none>   6m48s   v1.36.2-eks-254016e
    fargate-ip-192-168-165-70.eu-central-1.compute.internal   Ready    <none>   6m56s   v1.36.2-eks-254016e
    ip-192-168-51-213.eu-central-1.compute.internal           Ready    <none>   5h47m   v1.36.3-eks-cb19647
```

 
</details>


******

<details>
<summary>Create EKS cluster with eksctl</summary>
 <br />
 
 ### EKS Cluster Provisioning with eksctl

#### eksctl Installation and AWS Credential Configuration
Initiated the cluster deployment process by retrieving and installing the official `eksctl` binary for the Linux environment. Validated the installation and confirmed that the AWS CLI was properly configured with the required IAM credentials and target region (`eu-central-1`) to authorize infrastructure provisioning.
```bash
    root@PC:~/k8s-on-aws# curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
    root@PC:~/k8s-on-aws# sudo mv /tmp/eksctl /usr/local/bin
    root@PC:~/k8s-on-aws# eksctl version
    0.230.0
    root@PC:~/k8s-on-aws# aws configure list
    NAME       : VALUE                      : TYPE             : LOCATION
    profile    : <not set>                  : None             : None
    access_key : ****************UJWN       : shared-credentials-file :
    secret_key : ****************7sE6       : shared-credentials-file :
    region     : eu-central-1               : config-file      : ~/.aws/config
```
#### EKS Cluster Generation
Provisioned a managed Amazon EKS cluster named `demo-cluster`. Initially identified a version deprecation constraint (v1.27) and dynamically adjusted the target Kubernetes version to the supported v1.36. Configured the underlying EC2 compute infrastructure with a managed Node Group (`demo-nodes`) utilizing `t2.micro` instances and established auto-scaling boundaries (Min: 1, Max: 3, Desired: 2).
```bash
    root@PC:~/k8s-on-aws# eksctl create cluster \
    > --name demo-cluster \
    > --version 1.27 \
    > --region eu-central-1 \
    > --nodegroup-name demo-nodes \
    > --node-type t2.micro \
    > --nodes 2 \
    > --nodes-min 1 \
    > --nodes-max 3
    Error: resolving cluster version: invalid version, 1.27 is no longer supported, supported values: 1.31, 1.32, 1.33, 1.34, 1.35, 1.36
    see also: https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
    
    root@PC:~/k8s-on-aws# eksctl create cluster --name demo-cluster --version 1.36 --region eu-central-1 --nodegroup-name demo-nodes --node-type t2.micro --nodes 2 --nodes-min 1 --nodes-max 3
    2026-09-03 13:21:37 [ℹ]  eksctl version 0.230.0
    2026-09-03 13:21:37 [ℹ]  using region eu-central-1
    2026-09-03 13:21:38 [ℹ]  setting availability zones to [eu-central-1a eu-central-1b eu-central-1c]
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1a - public:192.168.0.0/19 private:192.168.96.0/19
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1b - public:192.168.32.0/19 private:192.168.128.0/19
    2026-09-03 13:21:38 [ℹ]  subnets for eu-central-1c - public:192.168.64.0/19 private:192.168.160.0/19
    2026-09-03 13:21:38 [ℹ]  nodegroup "demo-nodes" will use "" [AmazonLinux2023/1.36]
    2026-09-03 13:21:38 [ℹ]  using Kubernetes version 1.36
    2026-09-03 13:21:38 [ℹ]  creating EKS cluster "demo-cluster" in "eu-central-1" region with managed nodes
    2026-09-03 13:21:38 [ℹ]  will create 2 separate CloudFormation stacks for cluster itself and the initial managed nodegroup
    ...
    2026-09-03 13:21:38 [ℹ]  deploying stack "eksctl-demo-cluster-cluster"
    2026-09-03 13:22:08 [ℹ]  waiting for CloudFormation stack "eksctl-demo-cluster-cluster"
    ...
    2026-09-03 13:29:42 [ℹ]  creating addon: kube-proxy
    2026-09-03 13:29:42 [ℹ]  successfully created addon: kube-proxy
    2026-09-03 13:29:43 [ℹ]  creating addon: coredns
    2026-09-03 13:29:43 [ℹ]  successfully created addon: coredns
    ...
    2026-09-03 13:31:46 [ℹ]  deploying stack "eksctl-demo-cluster-nodegroup-demo-nodes"
    2026-09-03 13:31:46 [ℹ]  waiting for CloudFormation stack "eksctl-demo-cluster-nodegroup-demo-nodes"
    ...
    2026-09-03 13:34:00 [✔]  saved kubeconfig as "/root/.kube/config"
    2026-09-03 13:34:00 [✔]  all EKS cluster resources for "demo-cluster" have been created
    2026-09-03 13:34:00 [ℹ]  node "ip-192-168-26-26.eu-central-1.compute.internal" is ready
    2026-09-03 13:34:00 [ℹ]  node "ip-192-168-68-99.eu-central-1.compute.internal" is ready
    2026-09-03 13:34:00 [✔]  created 1 managed nodegroup(s) in cluster "demo-cluster"
    2026-09-03 13:34:01 [ℹ]  creating addon: metrics-server
    2026-09-03 13:34:03 [✔]  EKS cluster "demo-cluster" in "eu-central-1" region is ready
```
#### Post-Deployment Verification
Verified the successful registration of the worker nodes within the Kubernetes control plane. Both dynamically generated EC2 instances successfully joined the cluster and reported a `Ready` status.
```bash
    root@PC:~/k8s-on-aws# kubectl get nodes
    NAME                                             STATUS   ROLES    AGE   VERSION
    ip-192-168-26-26.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
    ip-192-168-68-99.eu-central-1.compute.internal   Ready    <none>   64m   v1.36.3-eks-cb19647
    
    root@PC:~/k8s-on-aws# kubectl get pod
    No resources found in default namespace.
```
#### AWS UI Visual Confirmations
Validated the CloudFormation stacks, newly provisioned VPC dependencies, active EKS Control Plane, and registered EC2 Node Groups directly through the AWS Management Console to ensure environment parity with the CLI.

<img width="1682" height="703" alt="image" src="https://github.com/user-attachments/assets/c9f66985-f3ed-4dcb-8ef0-72cafceee987" />
<img width="1710" height="831" alt="image" src="https://github.com/user-attachments/assets/11f22199-d010-458f-89a1-59fda926151f" />
<img width="1712" height="587" alt="image" src="https://github.com/user-attachments/assets/b07aecad-5d3b-4837-906c-05d3f4cbcd3c" />
<img width="1696" height="801" alt="image" src="https://github.com/user-attachments/assets/9b18ad68-c292-4ac2-975e-32bd1b416085" />
<img width="1694" height="823" alt="image" src="https://github.com/user-attachments/assets/e217309b-0775-4e09-a692-7d02217c810a" />



 
</details>


******

<details>
<summary>Deploy to EKS cluster from Jenkins Pipeline</summary>
 <br />
 
 ### Continuous Deployment Pipeline Setup for AWS EKS

#### Provisioning CLI Tools in the Jenkins Environment
Established an interactive, privileged shell session within the active Jenkins Docker container hosted on the DigitalOcean droplet. Downloaded, configured, and applied execution permissions to `kubectl` and `aws-iam-authenticator` binaries, placing them in the container's system path to enable direct communication with the Kubernetes control plane.

```bash
    root@PC:/mnt/c/Users/emrea# ssh root@164.90.179.224
    ...
    root@jenkins:~# docker ps
    CONTAINER ID   IMAGE                 COMMAND                  CREATED        STATUS         PORTS                                                                                      NAMES
    4b8376846d81   jenkins/jenkins:lts   "/usr/bin/tini -- /u…"   5 months ago   Up 4 minutes   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:50000->50000/tcp, [::]:50000->50000/tcp   wizardly_johnson
    
    root@jenkins:~# docker exec -u 0 -it 4b8376846d81 bash
    root@4b8376846d81:/# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl; chmod +x ./kubectl; mv ./kubectl /usr/local/bin/kubectl
    ...
    root@4b8376846d81:/# kubectl version
    Client Version: v1.31.0
    ...
    root@4b8376846d81:/# curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.11/aws-iam-authenticator_0.6.11_linux_amd64
    ...
    root@4b8376846d81:/# chmod +x ./aws-iam-authenticator
    root@4b8376846d81:/# mv ./aws-iam-authenticator /usr/local/bin/
```

#### Kubernetes Authentication Configuration
Generated the Kubernetes cluster configuration file containing the target EKS endpoint, certificate authority data, and AWS IAM authenticator execution arguments. Initialized the `.kube` directory within the Jenkins container's workspace (`/var/jenkins_home`) and securely transferred the configuration file from the host machine to authorize the Jenkins agent.
```bash
    root@jenkins:~# cat config
    apiVersion: v1
    kind: Config
    clusters:
    - cluster:
        certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUREVENDQWZXZ0F3SUJBZ0lRT2JreFpuYUNkSDVubWR2bHVITlNlekFOQmdrcWhraUc5dzBCQVFzRkFEQVYKTVJNd0VRWURWUVFERXdwcmRXSmxjbTVsZEdWek1CNFhEVEkyTURrd016RXdNakl4TlZvWERUTXhNRGt3TWpFdwpNakl4TlZvd0ZURVRNQkVHQTFVRUF4TUthM1ZpWlhKdVpYUmxjekNDQVNJd0RRWUpLb1pJaHZjTkFRRUJCUUFECmdnRVBBRENDQVFvQ2dnRUJBTWRsVklDYnc3WXhtaDIyajl2QzdMNDFlUnlDRFF3K2xzM2FYNW9BaHBLa00xVjcKbjhKR0QzMDVIaVg4cHVBdnpRck9GYWZTcTByKzZIRUEvSjZWZkN2YW9aRVJOTnV3TCtYSDBYSEFhRTBWUFlkQQpUY3FOZTRJeE5obGdCcTZiSXlKZWFuV0VrWGgxRWM2MXFoSE1nMEIwbFBSQUQ1U2trZmFSbjJvME43OEFSYmQ3CnRkWk9tQmtETUtnaFRuQjl5RC9mMlg5RTY2Y0I0UzJDNUxKUTI1SkdXdXFIV0RWMWZEU3A4M3pGcDBsTGw2clkKSjdBMlpYaFBXclVoNDRScGFFWVlVaFZ1QUZsZldGaEJXRDlScVFaWUdTWjVObjRtQUw2SDVOOHhhRnZ1bk82aQp1RDRFS3VlRWNWRC8xVmFqd0hZbHNsVzRaT2p6K0FBR3I3eXpVemtDQXdFQUFhTlpNRmN3RGdZRFZSMFBBUUgvCkJBUURBZ0trTUE4R0ExVWRFd0VCL3dRRk1BTUJBZjh3SFFZRFZSME9CQllFRkZQaDBUQjdaVStBS01hZ0xXWU8KODYyRUJvd2dNQlVHQTFVZEVRUU9NQXlDQ210MVltVnlibVYwWlhNd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dFQgpBRjRqQVdEc1BhaWp0ZnNOL3IwaGFNMUlIbGpBbm1sVktRUWhlYlMzbU1rWTExL1ErNm8zNmEvMFlYR3E1RWpECnVFTnJJUFVWaTBmRTVWSVRUZFdQOUtuWXcxZm9QWlNubHZiaWd5SWxoc3ZSNEgwQ3BSSG5xaHk1bUJxSEt0WTkKTHhBekZWajkxZjRBRTlVam40cE9WYUx1MFBBSVpzcE9kMkxZTXRuRHJkYVdyZUVIYlhMUUZaeCtKTU5VcWRLTgppTmZrOWMzUHhxYTJsc2luOVIrL1Y0MW4reTdxUU55Z2NFc2ZpNStEUjhzRkhHcUErb0VKT25hU0xIKzJ2Uno2Ck1BaThIQUgvcjExd3cxK0JaVkdSNUY3bEJRd05yVTlPcWdwY0NHK0NqVGFKMG9jc1Z6WWdhSTIrQldQanBKN2QKZ0FMWTNZZDdvV0NBUlVmV0lvNlFGeHc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
        server: https://5463C9E961ED09599F5BA27042808CF5.gr7.eu-central-1.eks.amazonaws.com
      name: kubernetes
    contexts:
    - context:
        cluster: kubernetes
        user: aws
      name: aws
    current-context: aws
    users:
    - name: aws
      user:
        exec:
          apiVersion: client.authentication.k8s.io/v1beta1
          command: /usr/local/bin/aws-iam-authenticator
          args:
            - "token"
            - "-i"
            - "demo-cluster"
    
    root@jenkins:~# docker exec -it 4b8376846d81 bash
    jenkins@4b8376846d81:/$ cd ~
    jenkins@4b8376846d81:~$ mkdir .kube
    jenkins@4b8376846d81:~$ exit
    
    root@jenkins:~# docker cp config 4b8376846d81:/var/jenkins_home/.kube/
    Successfully copied 3.58kB to 4b8376846d81:/var/jenkins_home/.kube/
```

#### Pipeline Definition and Credential Management
Configured encrypted AWS IAM credentials within the Jenkins dashboard to securely supply dynamic variables to the pipeline. Developed a declarative `Jenkinsfile` orchestrating a multi-stage CI/CD workflow, utilizing the `withCredentials` directive to authorize cluster access and execute a deployment resource creation on EKS.

<img width="1694" height="865" alt="image" src="https://github.com/user-attachments/assets/594b03d6-ad3c-47a5-818b-4a497dc7612b" />


```
    #!/usr/bin/env groovy
    
    pipeline {
        agent any
        stages {
            stage('build app') {
                steps {
                   script {
                       echo "building the application..."
                   }
                }
            }
            stage('build image') {
                steps {
                    script {
                        echo "building the docker image..."
                    }
                }
            }
            stage('deploy') {
                environment {
                    AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                    AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_access_secret_key')
                }
                steps {
                    script {
                       echo 'deploying docker image...'
                       sh 'kubectl create deployment nginx-deployment --image=nginx'
                    }
                }
            }
        }
    }
```

#### Pipeline Execution and Cluster Validation
Executed the Jenkins pipeline, successfully fetching the source code and progressing through the build and deployment stages. The Jenkins agent securely deployed the `nginx` container workload to the EKS cluster. Verified the instantiation of the managed pods via the local host's Kubernetes interface.

<img width="1024" height="385" alt="image" src="https://github.com/user-attachments/assets/1bfd0e90-a06b-43f5-a646-d96f8e0f89d2" />

```
    Started by user emre
    ...
    [Pipeline] { (deploy)
    [Pipeline] withCredentials
    Masking supported pattern matches of $AWS_ACCESS_KEY_ID or $AWS_SECRET_ACCESS_KEY
    [Pipeline] {
    [Pipeline] script
    [Pipeline] {
    [Pipeline] echo
    deploying docker image...
    [Pipeline] sh
    + kubectl create deployment nginx-deployment --image=nginx
    deployment.apps/nginx-deployment created
    [Pipeline] }
    ...
    Finished: SUCCESS
    
    root@PC:/mnt/c/Users/emrea# kubectl get pod
    NAME                                READY   STATUS    RESTARTS   AGE
    nginx-deployment-7d6869886d-bvbm6   0/1     Pending   0          4m52s
```

 
</details>


******

<details>
<summary>Complete CI/CD Pipeline with DockerHub</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Complete CI/CD Pipeline with AWS ECR</summary>
 <br />
 
 **content will be here**
 
</details>


******



