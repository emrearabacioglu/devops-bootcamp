******

<details>
<summary>Install Ansible</summary>
 <br />

### Demo Executed: Ansible Control Node on WSL

#### Installation
My WSL machine is the Ansible control node. Ansible is installed in a Python virtual environment of the module, together with the Python libraries needed by the AWS and Kubernetes modules (`boto3`, `kubernetes`) and `ansible-lint`. The collections used in the module projects are installed with `ansible-galaxy`.

```bash
    root@PC:~/modules/ansible# python3 -m venv .venv
    root@PC:~/modules/ansible# source .venv/bin/activate
    (.venv) root@PC:~/modules/ansible# pip install ansible boto3 botocore kubernetes ansible-lint
    (.venv) root@PC:~/modules/ansible# ansible-galaxy collection install amazon.aws community.docker community.general kubernetes.core
```

#### Verification
```bash
    (.venv) root@PC:~/modules/ansible# ansible --version
    ansible [core 2.21.5]
      config file = None
      ansible python module location = /root/modules/ansible/.venv/lib/python3.12/site-packages/ansible
      executable location = /root/modules/ansible/.venv/bin/ansible
      python version = 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0] (/root/modules/ansible/.venv/bin/python3)
      jinja version = 3.1.6
```


 
</details>

******

<details>
<summary>Setup Managed Server to Configure with Ansible</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Ansible Inventory and Ansible ad-hoc commands</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Configure AWS EC2 server with Ansible</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Managing Host Key Checking and SSH keys</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Introduction to Playbooks</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploy Nodejs application - Part 1</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploy Nodejs application - Part 2</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploy Nodejs application - Part 3</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Ansible Variables - make your Playbook customizable</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploy Nexus - Part 1</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploy Nexus - Part 2</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Ansible Configuration - Default Inventory File</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Run Docker applications - Part 1</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Run Docker applications - Part 2</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Terraform & Ansible</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Dynamic Inventory for EC2 Servers</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Deploying Application in K8s</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Run Ansible from Jenkins Pipeline - Part 1</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Run Ansible from Jenkins Pipeline - Part 2</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Project: Run Ansible from Jenkins Pipeline - Part 3</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Ansible Roles - Make your Ansible content more reusable and modular</summary>
 <br />

 content will be here

 
</details>

******

