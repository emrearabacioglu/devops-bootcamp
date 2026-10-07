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

### Demo Executed: First Playbook - Install and Remove nginx

#### Install nginx
The playbook runs on the `webserver` group of the inventory (2 droplets). It installs the latest nginx with the `apt` module and starts it with the `service` module.

```yaml
    ---
    - name: Configure nginx web server
      hosts: webserver
      tasks:
      - name: install nginx server
        apt:
          name: nginx
          state: latest
      - name: start nginx server
        service:
          name: nginx
          state: started
```

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ansible-playbook -i hosts my-playbook.yaml

    PLAY [Configure nginx web server] ****

    TASK [Gathering Facts] ****
    ok: [207.154.206.156]
    ok: [164.90.222.155]

    TASK [install nginx server] ****
    changed: [164.90.222.155]
    changed: [207.154.206.156]

    TASK [start nginx server] ****
    ok: [164.90.222.155]
    ok: [207.154.206.156]

    PLAY RECAP ****
    164.90.222.155             : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    207.154.206.156            : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

`Gathering Facts` runs automatically before the tasks and collects information about the servers. The `start` task returned `ok`, because the nginx package on Ubuntu already starts the service after installation.

#### Verification on the Server
```bash
    root@ubuntu-s-1vcpu-2gb-fra1-02:~# ps aux | grep nginx
    root        3791  0.0  0.3  11204  7052 ?        S    09:05   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
    www-data    3794  0.0  0.2  12892  4392 ?        S    09:05   0:00 nginx: worker process
    root@ubuntu-s-1vcpu-2gb-fra1-02:~# nginx -v
    nginx version: nginx/1.24.0 (Ubuntu)
```

#### Remove nginx
Changed the desired state to `absent` (package) and `stopped` (service) and ran the same playbook again.

```yaml
    ---
    - name: Configure nginx web server
      hosts: webserver
      tasks:
      - name: install nginx server
        apt:
          name: nginx
          state: absent
      - name: start nginx server
        service:
          name: nginx
          state: stopped
```

The first run removed nginx (`changed=1`). The second run made no changes (`changed=0`), because the servers were already in the desired state. Ansible is idempotent: it only changes what differs from the desired state.

```bash
    (.venv) root@PC:~/modules/ansible/00-basics# ansible-playbook -i hosts my-playbook.yaml
    ...
    PLAY RECAP ****
    164.90.222.155             : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    207.154.206.156            : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    (.venv) root@PC:~/modules/ansible/00-basics# ansible-playbook -i hosts my-playbook.yaml
    ...
    PLAY RECAP ****
    164.90.222.155             : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    207.154.206.156            : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

 
</details>

******

<details>
<summary>Project: Deploy Nodejs application - Part 1</summary>
 <br />

#### Preparation
* Created a new Ubuntu droplet on DigitalOcean (`188.166.34.20`) and added it to the inventory of the project.
* Took the Node.js application from the bootcamp repository and packaged it with `npm pack` into `nodejs-app-1.0.0.tgz`.

#### Playbook
The playbook has two plays:

* **Install node and npm** – updates the apt cache (skipped if it was updated in the last hour) and installs `nodejs` and `npm` with the `apt` module.
* **Deploy nodejs app** – the `unarchive` module copies the artifact from my machine to the server and unpacks it in `/root/`. The `src` path is relative to the playbook.

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /root/
```

#### Execution
```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml

    PLAY [Install node and npm] ****

    TASK [Gathering Facts] ****
    ok: [188.166.34.20]

    TASK [Update apt repo and cache] ****
    ok: [188.166.34.20]

    TASK [Install nodejs and npm] ****
    ok: [188.166.34.20]

    PLAY [Deploy nodejs app] ****

    TASK [Gathering Facts] ****
    ok: [188.166.34.20]

    TASK [Unpack the nodejs file] ****
    changed: [188.166.34.20]

    PLAY RECAP ****
    188.166.34.20              : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

#### Verification on the Server
`npm pack` puts the application into a `package` folder, so the app is unpacked to `/root/package`:

```bash
    root@ubuntu-s-1vcpu-1gb-ams3:~# ls
    package
    root@ubuntu-s-1vcpu-1gb-ams3:~# ls package/
    Dockerfile  Readme.md  app  package.json
```

 
</details>

******

<details>
<summary>Project: Deploy Nodejs application - Part 2</summary>
 <br />

### Demo Executed: Deploy Node.js Application - Install Dependencies and Start the App

#### Playbook
Extended the second play with three steps:

* **Install dependencies** – the `npm` module (`community.general` collection) runs `npm install` in the app folder and creates `node_modules`.
* **Start app** – the `command` module starts the app with `node server` in the `app` folder (`chdir`). The app runs in the foreground and never ends, so without `async` the task waits forever. My first run hung at this task and I had to stop it. With `async: 1000` and `poll: 0` Ansible starts the process and continues without waiting for it.
* **Display status** – `ps aux | grep node` needs a pipe, so it runs with the `shell` module. The output is saved with `register` and printed with `debug`.

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /root/
        - name: Install dependencies
          npm:
            path: /root/package
        - name: Start app
          command:
            chdir: /root/package/app/
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Unpack the nodejs file] ****
    ok: [188.166.34.20]

    TASK [Install dependencies] ****
    ok: [188.166.34.20]

    TASK [Start app] ****
    changed: [188.166.34.20]

    TASK [Display status] ****
    changed: [188.166.34.20]

    TASK [debug] ****
    ok: [188.166.34.20] => {
        "msg": [
            "root        8864  0.1  5.9 618624 59028 ?        Sl   11:22   0:00 node server",
            "root        9983  0.0  0.2   2804  1972 pts/1    S+   11:32   0:00 /bin/sh -c ps aux | grep node",
            "root        9985  0.0  0.2   7080  2160 pts/1    S+   11:32   0:00 grep node"
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=9    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

`command` and `shell` tasks are not idempotent: Ansible can't know what the command changes, so they report `changed` on every run.

#### Verification on the Server
```bash
    root@ubuntu-s-1vcpu-1gb-ams3:~/package# ls
    Dockerfile  Readme.md  app  node_modules  package-lock.json  package.json
    root@ubuntu-s-1vcpu-1gb-ams3:~/package# ps aux | grep node
    root        8864 11.8  6.3 618112 62808 ?        Sl   11:22   0:00 node server
```


 
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

