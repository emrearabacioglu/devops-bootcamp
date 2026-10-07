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

### Demo Executed: Host Key Checking for Long-lived and Ephemeral Servers

Ansible connects over SSH, so a server has to be in `~/.ssh/known_hosts` (host key) and my public key has to be in the server's `authorized_keys`. Otherwise the connection stops at the host key prompt, which Ansible can't answer.

#### Long-lived Server: Add the Host Key to known_hosts
Created a new droplet with my SSH key. The host key was added to `known_hosts` with `ssh-keyscan` (`-H` stores the host name hashed), and my public key was already in `authorized_keys` on the server.

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ssh-keyscan -H 159.223.12.8 >> ~/.ssh/known_hosts
    # 159.223.12.8:22 SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19
    (.venv) root@PC:~/modules/ansible/00-basics# ssh root@159.223.12.8
    root@ubuntu-s-1vcpu-2gb-ams3:~# cat .ssh/authorized_keys
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCscZcZ...3Q== root@PC
```

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ansible droplet -i hosts -m ping
    207.154.206.156 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    164.90.222.155 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    159.223.12.8 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
```

#### Ephemeral Servers: Disable Host Key Checking
For servers that are created and destroyed often, adding every host key manually is not practical. Host key checking was disabled in the user level Ansible config. (Ansible was installed with pip, so there is no `/etc/ansible` directory.)

```bash
    (.venv) root@PC:~/modules/ansible# cat ~/.ansible.cfg
    [defaults]
    host_key_checking = False
```

A new droplet (`206.189.2.121`) that is not in `known_hosts` was added to the inventory and reached without any host key prompt:

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# cat hosts
    [droplet]
    164.90.222.155
    207.154.206.156
    206.189.2.121

    [droplet:vars]
    ansible_ssh_private_key_file=/root/.ssh/id_rsa
    ansible_user=root
    ansible_python_interpreter=/usr/bin/python3.12

    (.venv) root@PC:~/modules/ansible/00-basics# ansible droplet -i hosts -m ping
    164.90.222.155 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    207.154.206.156 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    206.189.2.121 | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
```


 
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

