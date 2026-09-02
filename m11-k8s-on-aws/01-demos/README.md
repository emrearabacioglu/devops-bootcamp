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
 
 **content will be here**
 
</details>


******

<details>
<summary>Create EKS cluster with Fargate</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Create EKS cluster with eksctl</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Deploy to EKS cluster from Jenkins Pipeline</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Deploy to LKE cluster from Jenkins Pipeline</summary>
 <br />
 
 **content will be here**
 
</details>


******

<details>
<summary>Note on Best Practices - Credentials for different services in Jenkins</summary>
 <br />
 
 **content will be here**
 
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



