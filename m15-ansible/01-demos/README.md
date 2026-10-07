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
<summary>Ansible Inventory and Ansible ad-hoc commands</summary>
 <br />

### Demo Executed: Inventory File and Ad-hoc Commands

#### Managed Servers
Created 2 Ubuntu droplets on DigitalOcean with my SSH public key. These are the managed nodes, my WSL machine is the control node.

#### Inventory File
The servers are grouped as `droplet`. The SSH key and the user are defined once as group variables instead of repeating them on every host line.

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# cat hosts
    [droplet]
    164.90.222.155
    207.154.206.156

    [droplet:vars]
    ansible_ssh_private_key_file=/root/.ssh/id_rsa
    ansible_user=root
```

#### Ad-hoc Command
Ran the `ping` module on the whole group. It checks that Ansible can connect to the servers over SSH and use Python on them.

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ansible droplet -i hosts -m ping
    164.90.222.155 | SUCCESS => {
        "ansible_facts": {
            "discovered_interpreter_python": "/usr/bin/python3.12"
        },
        "changed": false,
        "ping": "pong"
    }
    207.154.206.156 | SUCCESS => {
        "ansible_facts": {
            "discovered_interpreter_python": "/usr/bin/python3.12"
        },
        "changed": false,
        "ping": "pong"
    }
```


 
</details>

******

<details>
<summary>Configure AWS EC2 server with Ansible</summary>
 <br />

### Demo Executed: Adding EC2 Instances to the Inventory

#### EC2 Instances
Created 2 EC2 instances (Amazon Linux 2023) with Terraform in the default VPC. My SSH public key was imported as the key pair, so the same private key works for the droplets and the EC2 instances.

#### Inventory File
Added the instances as a new group `ec2`. Amazon Linux uses `ec2-user` instead of `root`, and the Python interpreter on the servers is set explicitly.

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# cat hosts
    [droplet]
    164.90.222.155
    207.154.206.156

    [droplet:vars]
    ansible_ssh_private_key_file=/root/.ssh/id_rsa
    ansible_user=root

    [ec2]
    ec2-18-184-173-204.eu-central-1.compute.amazonaws.com
    ec2-3-79-111-198.eu-central-1.compute.amazonaws.com

    [ec2:vars]
    ansible_ssh_private_key_file=/root/.ssh/id_rsa
    ansible_user=ec2-user
    ansible_python_interpreter=/usr/bin/python3.9
```

#### Ad-hoc Command
```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ansible ec2 -i hosts -m ping
    ec2-18-184-173-204.eu-central-1.compute.amazonaws.com | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    ec2-3-79-111-198.eu-central-1.compute.amazonaws.com | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
```


 
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

