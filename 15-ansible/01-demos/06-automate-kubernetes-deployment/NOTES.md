# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate Kubernetes Deployment

### Demo Executed: Create an EKS Cluster with Terraform and Deploy an App into a New Namespace with Ansible

#### EKS Cluster
* The EKS cluster is created with the Terraform configuration from the Terraform module: a new VPC with public and private subnets, an EKS cluster (`myapp-eks-cluster`) and a managed node group with 3 worker nodes.
* After the cluster is up, a kubeconfig file for it is generated with the AWS CLI. The file is written into the project folder instead of the default `~/.kube/config`:

```bash
    aws eks update-kubeconfig --region eu-central-1 --name myapp-eks-cluster --kubeconfig ~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
```

#### Kubeconfig Environment Variable
The `kubernetes.core` modules read the kubeconfig path from the `K8S_AUTH_KUBECONFIG` environment variable, so the playbook doesn't need a `kubeconfig` parameter in each task:

```bash
    export K8S_AUTH_KUBECONFIG=~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
```

#### Playbook
* The play runs on `localhost`: the `kubernetes.core.k8s` module talks to the Kubernetes API from my machine, there is no SSH to the nodes.
* The first task creates the `my-app` namespace.
* The second task applies `nginx-config.yaml` (an nginx Deployment and a LoadBalancer Service) into that namespace.

`deploy-to-k8s.yaml`:

```yaml
    ---
    - name: Deploy app in new namespace
      hosts: localhost
      tasks:
        - name: Create k8s namespace
          kubernetes.core.k8s:
            name: my-app
            api_version: v1
            kind: Namespace
            state: present

        - name: Deploy nginx app
          kubernetes.core.k8s:
            src: ./nginx-config.yaml
            state: present
            namespace: my-app
```

#### Execution
First run, with only the namespace task. The namespace is created:

```bash
    (.venv) root@PC:~/modules/ansible/06-k8s-deployment (main)# ansible-playbook deploy-to-k8s.yaml

    PLAY [Deploy app in new namespace] ****

    TASK [Gathering Facts] ****
    ok: [localhost]

    TASK [Create k8s namespace] ****
    changed: [localhost]

    PLAY RECAP ****
    localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Second run, after adding the nginx task. The namespace already exists (`ok`), the nginx app is deployed (`changed`):

```bash
    (.venv) root@PC:~/modules/ansible/06-k8s-deployment (main)# ansible-playbook deploy-to-k8s.yaml

    PLAY [Deploy app in new namespace] ****

    TASK [Gathering Facts] ****
    ok: [localhost]

    TASK [Create k8s namespace] ****
    ok: [localhost]

    TASK [Deploy nginx app] ****
    changed: [localhost]

    PLAY RECAP ****
    localhost                  : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Run with the `K8S_AUTH_KUBECONFIG` variable. Everything is already in the desired state, so nothing changes:

```bash
    (.venv) root@PC:~/modules/ansible/06-k8s-deployment (main)# export K8S_AUTH_KUBECONFIG=~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
    (.venv) root@PC:~/modules/ansible/06-k8s-deployment (main)# ansible-playbook deploy-to-k8s.yaml

    PLAY [Deploy app in new namespace] ****

    TASK [Gathering Facts] ****
    ok: [localhost]

    TASK [Create k8s namespace] ****
    ok: [localhost]

    TASK [Deploy nginx app] ****
    ok: [localhost]

    PLAY RECAP ****
    localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

#### Verification in the Cluster
The namespace, the pod and the LoadBalancer service in the cluster:

```bash
    root@PC:~/modules/ansible/06-k8s-deployment (main)# export KUBECONFIG=~/modules/ansible/06-k8s-deployment/kubeconfig_myapp-eks-cluster
    root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get ns
    NAME              STATUS   AGE
    default           Active   34m
    kube-node-lease   Active   34m
    kube-public       Active   34m
    kube-system       Active   34m
    my-app            Active   2m52s

    root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get pod -n my-app
    NAME                     READY   STATUS    RESTARTS   AGE
    nginx-86c57bc6b8-4sv2f   1/1     Running   0          22s

    root@PC:~/modules/ansible/06-k8s-deployment (main)# kubectl get svc -n my-app
    NAME    TYPE           CLUSTER-IP       EXTERNAL-IP                                                                  PORT(S)        AGE
    nginx   LoadBalancer   172.20.230.120   a18b2faca56504aabb0b7821092280a2-2021946624.eu-central-1.elb.amazonaws.com   80:32464/TCP   38s
```
