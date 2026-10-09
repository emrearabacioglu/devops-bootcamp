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

### Demo Executed: Deploy Node.js Application - Run the App with a Dedicated Linux User

#### Playbook
Until now the app was deployed and started as `root`. To follow the least privilege principle, the app now runs with its own Linux user:

* **Create user for nodeapp** – a new play creates the user `nodeuser` with the `user` module.
* **Deploy nodejs app** – `become: True` and `become_user: nodeuser` run all tasks of this play as `nodeuser` (Ansible connects as `root` and switches the user with `sudo`). The artifact is unpacked to `/home/nodeuser` and the paths of the next tasks are adjusted.

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

    - name: Create user for nodeapp
      hosts: 188.166.34.20
      tasks:
        - name: Create linux user
          user:
            name: nodeuser
            comment: node admin
            group: admin

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      become: True
      become_user: nodeuser
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /home/nodeuser
        - name: Install dependencies
          npm:
            path: /home/nodeuser/package
        - name: Start app
          command:
            chdir: /home/nodeuser/package/app/
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
The `node server` process is now owned by `nodeuser`:

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Create linux user] ****
    changed: [188.166.34.20]

    PLAY [Deploy nodejs app] ****
    ...
    TASK [Unpack the nodejs file] ****
    changed: [188.166.34.20]

    TASK [Install dependencies] ****
    changed: [188.166.34.20]

    TASK [Start app] ****
    changed: [188.166.34.20]

    TASK [Display status] ****
    changed: [188.166.34.20]

    TASK [debug] ****
    ok: [188.166.34.20] => {
        "msg": [
            ...
            "nodeuser   10837 32.1  6.4 618064 63732 ?        Sl   11:49   0:00 node server",
            ...
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=11   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```


 
</details>

******

<details>
<summary>Ansible Variables - make your Playbook customizable</summary>
 <br />

### Demo Executed: Replace Hardcoded Values in the Node.js Playbook with Variables

#### Variables File
The app location, version, Linux user and home directory were hardcoded in several places of the playbook. I first defined them with `vars` inside the play, then moved them to a separate file, `project-vars`, so the same playbook can be used with different values. A variable can also use another variable (`user_home_dir`).

```yaml
    location: nodejs-app
    version: 1.0.0
    linux_name: nodeuser
    user_home_dir: /home/{{linux_name}}
```

#### Playbook
The plays load the file with `vars_files` and use the values with `{{ }}`. A value that starts with a variable must be in quotes, otherwise YAML reads `{` as the start of a dictionary.

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

    - name: Create user for nodeapp
      hosts: 188.166.34.20
      vars_files:
        project-vars
      tasks:
        - name: Create linux user
          user:
            name: "{{linux_name}}"
            comment: node admin
            group: admin

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      become: True
      become_user: "{{linux_name}}"
      vars_files:
        project-vars
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: "{{location}}/nodejs-app-{{version}}.tgz"
            dest: "{{user_home_dir}}"
        - name: Install dependencies
          npm:
            path: "{{user_home_dir}}/package"
        - name: Start app
          command:
            chdir: "{{user_home_dir}}/package/app/"
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
The result is the same as before. The user, the files and the dependencies already existed, so only the `command` and `shell` tasks report `changed`.

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Create linux user] ****
    ok: [188.166.34.20]

    PLAY [Deploy nodejs app] ****
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
            ...
            "nodeuser   12977  0.1  5.9 618312 58692 ?        Sl   13:00   0:00 node server",
            ...
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=11   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

 
</details>

******

<details>
<summary>Project: Deploy Nexus - Part 1</summary>
 <br />

### Demo Executed: Deploy Nexus - Install Java and Unpack the Nexus Installer

#### Preparation
Created a new Ubuntu droplet on DigitalOcean (`206.189.51.31`) for Nexus and added it to the inventory of the project. The playbook automates the manual Nexus installation steps.

#### Playbook
* **Install java and net-tools** – Nexus 3.70.1 and later needs Java 17, so `openjdk-17-jre-headless` is installed instead of Java 8. `net-tools` provides `netstat` to check the Nexus port later.
* **Download/Unpack Nexus Installer**:
    * `get_url` downloads the latest Nexus to `/opt/`. The result is saved with `register`, so the next task can use the downloaded file path (`download_result.dest`).
    * `unarchive` with `remote_src: yes` unpacks the file that is already on the server (by default it copies the file from my machine).
    * The unpacked folder name contains the Nexus version, which changes with every release. `find` gets the folder name, so it is not hardcoded.
    * The folder is renamed to `/opt/nexus` with `mv`. `stat` checks if `/opt/nexus` already exists and `when` skips the task in that case, so the `shell` task doesn't fail on the next run.

```yaml
    ---
    - name: Install java and net-tools
      hosts: 206.189.51.31
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600

        - name: Install Java 17
          apt: name=openjdk-17-jre-headless

        - name: Install net-tools
          apt: name=net-tools

    - name: Download/Unpack Nexus Installer
      hosts: 206.189.51.31
      tasks:
        - name: Download Nexus
          get_url:
            url: https://download.sonatype.com/nexus/3/latest-linux-x86_64.tar.gz
            dest: /opt/
          register: download_result

        - name: Untar Nexus Installer
          unarchive:
            src: "{{download_result.dest}}"
            dest: /opt/
            remote_src: yes

        - name: Find nexus folder
          find:
            paths: /opt/
            pattern: "nexus-*"
            file_type: directory
          register: find_result

        - name: Check if nexus folder stats
          stat:
            path: /opt/nexus
          register: stat_result

        - name: Rename nexus folder
          shell: mv {{find_result.files[0].path}} /opt/nexus
          when: not stat_result.stat.exists
```

#### Execution
The folder was already renamed in an earlier run, so the rename task is skipped:

```bash
    (.venv) root@PC:~/modules/ansible/02-nexus# ansible-playbook -i hosts deploy-nexus.yaml
    ...
    PLAY [Download/Unpack Nexus Installer] ****
    ...
    TASK [Download Nexus] ****
    ok: [206.189.51.31]

    TASK [Untar Nexus Installer] ****
    changed: [206.189.51.31]

    TASK [Find nexus folder] ****
    ok: [206.189.51.31]

    TASK [Check if nexus folder stats] ****
    ok: [206.189.51.31]

    TASK [Rename nexus folder] ****
    skipping: [206.189.51.31]

    PLAY RECAP ****
    206.189.51.31              : ok=9    changed=1    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

 
</details>

******

<details>
<summary>Project: Deploy Nexus - Part 2</summary>
 <br />

### Demo Executed: Deploy Nexus - Nexus User, Start and Verify

#### Changes in the Existing Plays
* The servers are now targeted with the inventory group `nexus_server` instead of the IP address.
* The inventory file is defined in the project's `ansible.cfg`, so the playbook runs without `-i hosts`.
* The `stat` check moved to the beginning of the play. The archive is unpacked only if `/opt/nexus` doesn't exist, so a second run doesn't create a new `nexus-3.x` folder.

#### New Plays
* **Create nexus user and group** – the `group` and `user` modules create the `nexus` user. The `file` module with `recurse: yes` gives the ownership of the `nexus` and `sonatype-work` folders to this user.
* **Start nexus with nexus user** – the play runs as `nexus` (`become_user`). In the Nexus version I installed (3.96) there is no `nexus.rc` file anymore, the `run_as_user` setting is in the `bin/nexus` script. `lineinfile` replaces the line `run_as_user=''` with `run_as_user="nexus"`, so Nexus also switches to the `nexus` user when it is started as root.
* **Verify nexus running** – checks the process with `ps`. Nexus needs a few minutes to start, so `wait_for` waits until port `8081` is open (max. 5 minutes) instead of a fixed pause. Then `netstat` shows the open port.

```yaml
    ---
    - name: Install java and net-tools
      hosts: nexus_server
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600

        - name: Install Java 17
          apt: name=openjdk-17-jre-headless

        - name: Install net-tools
          apt: name=net-tools

    - name: Download/Unpack Nexus Installer
      hosts: nexus_server
      tasks:
        - name: Check nexus folder stats
          stat:
            path: /opt/nexus
          register: stat_result

        - name: Download Nexus
          get_url:
            url: https://download.sonatype.com/nexus/3/latest-linux-x86_64.tar.gz
            dest: /opt/
          register: download_result

        - name: Untar Nexus Installer
          unarchive:
            src: "{{download_result.dest}}"
            dest: /opt/
            remote_src: yes
          when: not stat_result.stat.exists

        - name: Find nexus folder
          find:
            paths: /opt/
            pattern: "nexus-*"
            file_type: directory
          register: find_result

        - name: Rename nexus folder
          shell: mv {{find_result.files[0].path}} /opt/nexus
          when: not stat_result.stat.exists

    - name: Create nexus user and group
      hosts: nexus_server
      tasks:
        - name: Create nexus group
          group:
            name: nexus
            state: present

        - name: Create nexus user
          user:
            name: nexus
            group: nexus

        - name: Match user and group of nexus folder
          file:
            path: /opt/nexus
            state: directory
            owner: nexus
            group: nexus
            recurse: yes

        - name: Match user and group of sonatype folder
          file:
            path: /opt/sonatype-work
            state: directory
            owner: nexus
            group: nexus
            recurse: yes

    - name: Start nexus with nexus user
      hosts: nexus_server
      become: True
      become_user: nexus
      tasks:
        - name: Set run_as_user nexus
          lineinfile:
            path: /opt/nexus/bin/nexus
            regexp: '^run_as_user='
            line: run_as_user="nexus"

        - name: Run nexus
          command: /opt/nexus/bin/nexus start

    - name: Verify nexus running
      hosts: nexus_server
      tasks:
        - name: Check with ps
          shell: ps aux | grep nexus
          register: app_status
        - debug: msg={{app_status.stdout_lines}}

        - name: Wait for nexus port
          wait_for:
            port: 8081
            timeout: 300

        - name: Check with netstat
          shell: netstat -lnpt
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
Nexus runs as the `nexus` user and listens on port `8081`:

```bash
    (.venv) root@PC:~/modules/ansible/02-nexus# ansible-playbook deploy-nexus.yaml
    ...
    PLAY [Start nexus with nexus user] ****
    ...
    TASK [Set run_as_user nexus] ****
    ok: [165.22.31.85]

    TASK [Run nexus] ****
    changed: [165.22.31.85]

    PLAY [Verify nexus running] ****
    ...
    TASK [debug] ****
    ok: [165.22.31.85] => {
        "msg": [
            "nexus       2025  104 31.3 6802596 2548640 ?     Sl   16:36   6:29 /opt/nexus/jdk/temurin_21.0.11_10_linux_x86_64/jdk-21.0.11+10/bin/java -server ... -jar /opt/nexus/bin/sonatype-nexus-repository-3.96.4-01.jar",
            ...
        ]
    }

    TASK [Wait for nexus port] ****
    ok: [165.22.31.85]

    TASK [Check with netstat] ****
    changed: [165.22.31.85]

    TASK [debug] ****
    ok: [165.22.31.85] => {
        "msg": [
            "Active Internet connections (only servers)",
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    ",
            "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1/init              ",
            "tcp6       0      0 :::8081                 :::*                    LISTEN      2025/java           ",
            ...
        ]
    }

    PLAY RECAP ****
    165.22.31.85               : ok=22   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```


 
</details>

******

<details>
<summary>Project: Run Docker applications</summary>
 <br />

### Demo Executed: Install Docker and Docker Compose and Start the Containers with Ansible

#### Preparation
* Created an EC2 instance (Amazon Linux 2023) with Terraform in the default VPC. The security group allows SSH from my IP and port `8080` for the application.
* Built the Java application image and pushed it to a private Docker Hub repository (`emrearabacioglu/java-mysql-app:1.0`).

#### Playbook
* **Install Docker** – installs Docker with the `yum` module and starts the Docker daemon with `systemd`.
* **Create new user** – creates `dockeruser` and adds it to the `docker` group, so the containers don't run with the default `ec2-user`.
* **Install docker-compose** – runs as `dockeruser`. Docker Compose is not in the Amazon Linux repository, so the Compose plugin is downloaded from the GitHub releases to `~/.docker/cli-plugins`. The download URL needs the CPU architecture of the server, which comes from `uname -m`.
* **Start docker containers** – copies the compose file to the server, logs in to Docker Hub with `docker_login` (the password comes from the variables file) and starts the containers with `docker_compose_v2`.

```yaml
    ---
    - name: Install Docker
      hosts: docker_server
      become: yes
      tasks:
        - name: Install Docker
          yum:
            name: docker
            update_cache: yes
            state: present

        - name: Start docker daemon
          systemd:
            name: docker
            state: started

    - name: Create new user
      hosts: docker_server
      vars_files: project-vars
      become: yes
      tasks:
        - name: Create new user
          user:
            name: dockeruser
            groups: "{{user_groups}}"
            append: yes

    - name: Install docker-compose
      hosts: docker_server
      become: yes
      become_user: dockeruser
      tasks:
        - name: Create docker-compose directory
          file:
            path: ~/.docker/cli-plugins
            state: directory

        - name: Get arcthitecture of remote machine
          shell: uname -m
          register: remote_arch

        - name: Install docker-compose
          get_url:
            url: "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-{{remote_arch.stdout}}"
            dest: ~/.docker/cli-plugins/docker-compose
            mode: +x

    - name: Start docker containers
      hosts: docker_server
      become: yes
      become_user: dockeruser
      vars_files: project-vars
      tasks:
        - name: copy docker compose
          copy:
            src: docker-compose.yaml
            dest: /home/dockeruser/docker-compose.yaml

        - name: Docker login
          docker_login:
            username: emrearabacioglu
            password: "{{docker_password}}"

        - name: Start containers
          community.docker.docker_compose_v2:
            project_src: /home/dockeruser
```

#### Execution
The playbook was executed on a new server:

```bash
    (.venv) root@PC:~/modules/ansible/03-docker# ansible-playbook deploy-docker.yaml

    PLAY [Install Docker] ****

    TASK [Gathering Facts] ****
    ok: [3.73.116.21]

    TASK [Install Docker] ****
    changed: [3.73.116.21]

    TASK [Start docker daemon] ****
    changed: [3.73.116.21]

    PLAY [Create new user] ****
    ...
    TASK [Create new user] ****
    changed: [3.73.116.21]

    PLAY [Install docker-compose] ****
    ...
    TASK [Create docker-compose directory] ****
    changed: [3.73.116.21]

    TASK [Get arcthitecture of remote machine] ****
    changed: [3.73.116.21]

    TASK [Install docker-compose] ****
    changed: [3.73.116.21]

    PLAY [Start docker containers] ****
    ...
    TASK [copy docker compose] ****
    changed: [3.73.116.21]

    TASK [Docker login] ****
    changed: [3.73.116.21]

    TASK [Start containers] ****
    changed: [3.73.116.21]

    PLAY RECAP ****
    3.73.116.21                : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

#### Verification on the Server
```bash
    [ec2-user@ip-172-31-40-163 ~]$ sudo docker ps
    CONTAINER ID   IMAGE                                COMMAND                  CREATED              STATUS              PORTS                                                  NAMES
    00062373a8fc   emrearabacioglu/java-mysql-app:1.0   "/__cacert_entrypoin…"   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp              my-java-app
    2a847c1ca772   phpmyadmin                           "/docker-entrypoint.…"   About a minute ago   Up About a minute   0.0.0.0:8083->80/tcp, :::8083->80/tcp                  myadmin
    e05688155b87   mysql                                "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql
```


 
</details>

******

<details>
<summary>Project: Terraform & Ansible</summary>
 <br />

### Demo Executed: Run the Ansible Playbook Automatically after Terraform Creates the Servers

#### Terraform Configuration
The servers from the previous project are now configured automatically. Once Terraform creates the EC2 instances, it runs the Ansible playbook:

* `count = 2` creates two instances in the default VPC.
* A `null_resource` with a `local-exec` provisioner runs `ansible-playbook` on my machine. `working_dir` points to the parent folder where the playbook and the Ansible files are.
* The public IPs of all instances are passed with `join()` directly as the inventory (the trailing comma tells Ansible it is a host list, not a file). The SSH key and the user are given on the command line.
* `triggers` uses the same IP list, so the playbook runs again when the instances change.

```hcl
    provider "aws" {
      region = "eu-central-1"
    }

    variable instance_type {}
    variable my_ip {}
    variable public_key_location {}
    variable ssh_key_private {}

    data "aws_ami" "amazon-linux-image" {
      most_recent = true
      owners      = ["amazon"]

      filter {
        name   = "name"
        values = ["al2023-ami-2023.*-x86_64"]
      }

      filter {
        name   = "virtualization-type"
        values = ["hvm"]
      }
    }

    # default VPC (no vpc_id given)
    resource "aws_security_group" "ansible-sg" {
      name = "ansible-sg"

      ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = [var.my_ip]
      }

      ingress {
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }

      egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
      }
    }

    resource "aws_key_pair" "ssh-key" {
      key_name   = "ansible-key"
      public_key = file(var.public_key_location)
    }

    resource "aws_instance" "ansible-server" {
      count                  = 2
      ami                    = data.aws_ami.amazon-linux-image.id
      instance_type          = var.instance_type
      key_name               = aws_key_pair.ssh-key.key_name
      vpc_security_group_ids = [aws_security_group.ansible-sg.id]

      tags = {
        Name = "ansible-server-${count.index + 1}"
      }
    }

    resource "null_resource" "configure_server" {
      triggers = {
        trigger = join(",", aws_instance.ansible-server[*].public_ip)
      }
      provisioner "local-exec"{
        working_dir = "${path.module}/.."
        command     = "ansible-playbook --inventory ${join(",", aws_instance.ansible-server[*].public_ip)}, --private-key ${var.ssh_key_private} --user ec2-user deploy-docker.yaml"
      }
    }

    output "server-ips" {
      value = aws_instance.ansible-server[*].public_ip
    }
```

#### Playbook Changes
The playbook is the same as in the previous project, with two changes:

* All plays use `hosts: all`, because the inventory now comes from Terraform and has no groups.
* A new first play waits until SSH is available. A new EC2 instance is "running" before its SSH server is ready, so without this play the next tasks could fail. The task runs on my machine (`ansible_connection: local`) and checks port 22 of each server with `wait_for`.

```yaml
    ---
    - name: Wait SSH connection
      hosts: all
      gather_facts: False
      tasks:
        - name: Wait SSH connection
          wait_for:
            port: 22
            delay: 10
            timeout: 120
            search_regex: OpenSSH
            host: '{{ (ansible_ssh_host|default(ansible_host))|default(inventory_hostname) }}'
          vars:
            ansible_connection: local
            ansible_python_interpreter: /usr/bin/python3

    - name: Install Docker
      hosts: all
      ...
```

#### Execution
A single `terraform apply` creates the servers and configures both of them:

```bash
    (.venv) root@PC:~/modules/ansible/04-terraform-integration/terraform# terraform apply --auto-approve
    ...
    Plan: 5 to add, 0 to change, 0 to destroy.
    ...
    aws_instance.ansible-server[1]: Creation complete after 14s [id=i-0fcae013c9e0a07cc]
    aws_instance.ansible-server[0]: Creation complete after 14s [id=i-0a50bcca48ccf8111]
    null_resource.configure_server: Creating...
    null_resource.configure_server: Provisioning with 'local-exec'...
    null_resource.configure_server (local-exec): Executing: ["/bin/sh" "-c" "ansible-playbook --inventory 18.185.112.89,63.177.48.188, --private-key /root/.ssh/id_rsa --user ec2-user deploy-docker.yaml"]

    null_resource.configure_server (local-exec): PLAY [Wait SSH connection] ****

    null_resource.configure_server (local-exec): TASK [Wait SSH connection] ****
    null_resource.configure_server (local-exec): ok: [18.185.112.89]
    null_resource.configure_server (local-exec): ok: [63.177.48.188]
    ...
    null_resource.configure_server (local-exec): TASK [Start containers] ****
    null_resource.configure_server (local-exec): changed: [18.185.112.89]
    null_resource.configure_server (local-exec): changed: [63.177.48.188]

    null_resource.configure_server (local-exec): PLAY RECAP ****
    null_resource.configure_server (local-exec): 18.185.112.89              : ok=14   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    null_resource.configure_server (local-exec): 63.177.48.188              : ok=14   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    null_resource.configure_server: Creation complete after 2m46s [id=3444770605447531667]

    Apply complete! Resources: 5 added, 0 changed, 0 destroyed.

    Outputs:

    server-ips = [
      "18.185.112.89",
      "63.177.48.188",
    ]
```

#### Verification on the Server
```bash
    [ec2-user@ip-172-31-34-32 ~]$ sudo docker ps
    CONTAINER ID   IMAGE                                COMMAND                  CREATED          STATUS          PORTS                                                  NAMES
    f88e6b63e99b   emrearabacioglu/java-mysql-app:1.0   "/__cacert_entrypoin…"   16 seconds ago   Up 2 seconds    0.0.0.0:8080->8080/tcp, :::8080->8080/tcp              my-java-app
    e42c069e3c23   mysql                                "docker-entrypoint.s…"   16 seconds ago   Up 14 seconds   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql
    56f3daa09d35   phpmyadmin                           "/docker-entrypoint.…"   16 seconds ago   Up 14 seconds   0.0.0.0:8083->80/tcp, :::8083->80/tcp                  myadmin
```


 
</details>

******

<details>
<summary>Dynamic Inventory for EC2 Servers</summary>
 <br />

 ### Demo Executed: Use the aws_ec2 Inventory Plugin Instead of a Static Hosts File

#### Infrastructure
The EC2 instances are created with Terraform in the default VPC, in a few steps:

* First 3 servers were created, and the playbook configured all of them through the dynamic inventory.
* A 4th server was added. The next `ansible-inventory` run listed it automatically, without editing any file.
* Finally the servers were tagged as 2 `dev-server` and 2 `prod-server`, so they can be grouped by tag.

#### Inventory Plugin Configuration
The `aws_ec2` plugin (from the `amazon.aws` collection, uses `boto3`) queries AWS for the running instances. The config file name must end with `aws_ec2.yaml`.

* `keyed_groups` creates groups dynamically: one group per Name tag value (`tag_Name_...`) and one per instance type (`instance_type_...`).
* In the default VPC the instances have public DNS names, so the plugin uses them as host names.

```yaml
    ---
    plugin : aws_ec2
    regions:
      - eu-central-1

    keyed_groups:
      - key: tags
        prefix: tag

      - key: instance_type
        prefix: instance_type
```

`ansible.cfg` uses the plugin file as the default inventory and sets the SSH user and key for all servers, so no `-i` or connection parameters are needed:

```properties
    [defaults]
    host_key_checking = False
    inventory = inventory_aws_ec2.yaml

    enable_plugins = aws_ec2

    remote_user = ec2-user
    private_key_file = /root/.ssh/id_rsa
```

#### Dynamic Groups
```bash
    (.venv) root@PC:~/modules/ansible/05-dynamic-inventory (main)# ansible-inventory -i inventory_aws_ec2.yaml --graph
    @all:
      |--@ungrouped:
      |--@aws_ec2:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
      |--@tag_Name_prod_server:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |--@instance_type_t3_small:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
      |--@tag_Name_dev_server:
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
```

#### Playbook
The playbook is the same as in the Terraform & Ansible project. Only the target changed: all plays use the dynamic group `tag_Name_dev_server`, so only the dev servers are configured.

```yaml
    ---
    - name: Wait SSH connection
      hosts: tag_Name_dev_server
      gather_facts: False
      tasks:
        - name: Wait SSH connection
          wait_for:
            port: 22
            delay: 10
            timeout: 120
            search_regex: OpenSSH
            host: '{{ (ansible_ssh_host|default(ansible_host))|default(inventory_hostname) }}'
          vars:
            ansible_connection: local
            ansible_python_interpreter: /usr/bin/python3

    - name: Install Docker
      hosts: tag_Name_dev_server
      become: yes
      ...

    - name: Start docker containers
      hosts: tag_Name_dev_server
      become: yes
      become_user: dockeruser
      vars_files: project-vars
      ...
```

#### Execution
Only the 2 dev servers are targeted; the prod servers are skipped:

```bash
    (.venv) root@PC:~/modules/ansible/05-dynamic-inventory (main)# ansible-playbook deploy-docker-dynamic.yaml

    PLAY [Wait SSH connection] ****

    TASK [Wait SSH connection] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]

    PLAY [Install Docker] ****

    TASK [Gathering Facts] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]

    TASK [Install Docker] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]
    ...
    PLAY [Start docker containers] ****
    ...
    TASK [Start containers] ****
    changed: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]
    changed: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]

    PLAY RECAP ****
    ec2-35-159-49-8.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ec2-63-181-5-198.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```


 
</details>

******

<details>
<summary>Project: Deploying Application in K8s</summary>
 <br />

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


Run with the  `K8S_AUTH_KUBECONFIG` variable. Everything is already in the desired state, so nothing changes:

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


 
</details>

******

<details>
<summary>Project: Run Ansible from Jenkins Pipeline</summary>
 <br />

### Demo Executed: Configure EC2 Instances with Ansible from a Jenkins Pipeline

#### Infrastructure
* **Jenkins server:** DigitalOcean droplet, Jenkins runs in a Docker container.
* **Ansible control node:** a separate DigitalOcean droplet (Ubuntu). AWS credentials are configured on it, so the `aws_ec2` inventory plugin can query the EC2 instances.
* **Ansible managed nodes:** 2 EC2 instances (Amazon Linux 2023) created with Terraform in the default VPC.
    * A dedicated key pair (`ansible-jenkins`) is used for the EC2 instances instead of my personal SSH key, because its private key is stored in Jenkins and copied to the control node.
    * The security group allows SSH from my IP and from the Ansible control node.

#### Jenkins Configuration
* **Plugins:** SSH Agent (`sshagent`) and SSH Pipeline Steps (`sshScript`, `sshCommand`).
* **Credentials** (SSH Username with private key):
    * `ansible-server-key`: user `root` + private key for the Ansible control node.
    * `ec2-server-key`: user `ec2-user` + private key of the `ansible-jenkins` key pair.
* **Pipeline job:** "Pipeline script from SCM" with my bootcamp repo. The Jenkinsfile is in a subfolder, so it is set with **Script Path** (`07-jenkins-integration/java-maven-app/Jenkinsfile`). The pipeline runs in the repo root, so all file paths in the Jenkinsfile start from there.

#### Jenkinsfile
* **Stage 1:** copies the Ansible files (`ansible.cfg`, inventory, playbook) to the control node with `scp`, using `sshagent`. Then it copies the EC2 private key from the `ec2-server-key` credential to `/root/ssh-key.pem`.
* **Stage 2:** connects to the control node with SSH Pipeline Steps:
    * `sshScript` runs `prepare-ansible-server.sh`, which installs Ansible and Boto3 on the control node.
    * `sshCommand` runs `ansible-playbook` on the control node.
* The control node IP is defined once as an environment variable (`ANSIBLE_SERVER`).

```groovy
    pipeline {
        agent any
        environment {
            ANSIBLE_SERVER = "164.92.224.167"
        }
        stages {
            stage("Copy files to ansible-server") {
                steps {
                    script {
                        echo "copying necessary files to ansible control node"
                        sshagent(['ansible-server-key']) {
                            sh "scp -o StrictHostKeyChecking=no 07-jenkins-integration/java-maven-app/ansible/* root@${ANSIBLE_SERVER}:/root"
                            withCredentials([sshUserPrivateKey(credentialsId: 'ec2-server-key', keyFileVariable: 'keyfile', usernameVariable: 'user')]) {
                                sh 'scp $keyfile root@$ANSIBLE_SERVER:/root/ssh-key.pem'
                            }
                        }
                    }
                }
            }
            stage("Configure EC2 instances with ansible") {
                steps {
                    script {
                        echo "calling ansible playbook to config ec2 instances"
                        def remote = [:]
                        remote.name = "ansible-server"
                        remote.host = ANSIBLE_SERVER
                        remote.allowAnyHosts = true
                        withCredentials([sshUserPrivateKey(credentialsId: 'ansible-server-key', keyFileVariable: 'keyfile', usernameVariable: 'user')]) {
                            remote.user = user
                            remote.identityFile = keyfile
                            sshScript remote: remote, script : "07-jenkins-integration/java-maven-app/prepare-ansible-server.sh"
                            sshCommand remote: remote, command: "ansible-playbook jenkins-playbook.yaml"
                        }
                    }
                }
            }
        }
    }
```

`prepare-ansible-server.sh`:

```bash
    #!/usr/bin/env bash

    apt update
    apt install ansible -y
    apt install python3-boto3 -y
```

#### Ansible Files
`ansible.cfg` uses the dynamic inventory and the EC2 key that Jenkins copied to the control node:

```properties
    [defaults]
    host_key_checking = False
    inventory = inventory_aws_ec2.yaml

    enable_plugins = aws_ec2

    remote_user = ec2-user
    private_key_file = ~/ssh-key.pem
```

`inventory_aws_ec2.yaml`:

```yaml
    ---
    plugin : aws_ec2
    regions:
      - eu-central-1

    keyed_groups:
      - key: tags
        prefix: tag
      - key: instance_type
        prefix: instance_type
```

`jenkins-playbook.yaml` installs Docker and Docker Compose on all EC2 instances:

```yaml
    ---
    - name: Install Docker
      hosts: all
      become: yes
      tasks:
        - name: Install Docker
          yum:
            name: docker
            update_cache: yes
            state: present

        - name: Start docker daemon
          systemd:
            name: docker
            state: started

    - name: Install docker-compose
      hosts: all
      tasks:
        - name: Create docker-compose directory
          file:
            path: ~/.docker/cli-plugins
            state: directory

        - name: Get arcthitecture of remote machine
          shell: uname -m
          register: remote_arch

        - name: Install docker-compose
          get_url:
            url: "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-{{remote_arch.stdout}}"
            dest: ~/.docker/cli-plugins/docker-compose
            mode: +x
```

#### Pipeline Execution
```bash
    Started by user emre
    Obtained 07-jenkins-integration/java-maven-app/Jenkinsfile from git https://github.com/emrearabacioglu/ansible.git
    ...
    Checking out Revision 8874e49b06718234991223b0c087dedd20bb328e (refs/remotes/origin/main)
    ...
    [Pipeline] { (Copy files to ansible-server)
    copying necessary files to ansible control node
    [ssh-agent] Using credentials root
    ...
    + scp -o StrictHostKeyChecking=no 07-jenkins-integration/java-maven-app/ansible/ansible.cfg 07-jenkins-integration/java-maven-app/ansible/inventory_aws_ec2.yaml 07-jenkins-integration/java-maven-app/ansible/jenkins-playbook.yaml root@164.92.224.167:/root
    [Pipeline] withCredentials
    Masking supported pattern matches of $keyfile
    + scp **** root@164.92.224.167:/root/ssh-key.pem
    ...
    [Pipeline] { (Configure EC2 instances with ansible)
    calling ansible playbook to config ec2 instances
    [Pipeline] sshScript
    Executing script on ansible-server[164.92.224.167]: /var/jenkins_home/workspace/ansible-pipeline/07-jenkins-integration/java-maven-app/prepare-ansible-server.sh
    ...
    ansible is already the newest version (9.2.0+dfsg-0ubuntu5).
    ...
    python3-boto3 is already the newest version (1.34.46+dfsg-1ubuntu1).
    [Pipeline] sshCommand
    Executing command on ansible-server[164.92.224.167]: ansible-playbook jenkins-playbook.yaml sudo: false

    PLAY [Install Docker] ****

    TASK [Gathering Facts] ****
    ok: [ec2-18-156-36-106.eu-central-1.compute.amazonaws.com]
    ok: [ec2-3-121-232-17.eu-central-1.compute.amazonaws.com]

    TASK [Install Docker] ****
    changed: [ec2-18-156-36-106.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-121-232-17.eu-central-1.compute.amazonaws.com]

    TASK [Start docker daemon] ****
    changed: [ec2-3-121-232-17.eu-central-1.compute.amazonaws.com]
    changed: [ec2-18-156-36-106.eu-central-1.compute.amazonaws.com]

    PLAY [Install docker-compose] ****
    ...
    TASK [Install docker-compose] ****
    changed: [ec2-18-156-36-106.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-121-232-17.eu-central-1.compute.amazonaws.com]

    PLAY RECAP ****
    ec2-18-156-36-106.eu-central-1.compute.amazonaws.com : ok=7    changed=5    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ec2-3-121-232-17.eu-central-1.compute.amazonaws.com : ok=7    changed=5    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    Finished: SUCCESS
```

<img width="1144" height="458" alt="image" src="https://github.com/user-attachments/assets/32aaad53-0835-4e44-b580-d693c2d8fbe2" />


#### Verification
Files copied by Jenkins to the Ansible control node:

```bash
    root@PC:~/modules/ansible (main)# ssh root@164.92.224.167 "ls -la /root"
    ...
    -rw-r--r--  1 root root  154 Oct  9 09:47 ansible.cfg
    -rw-r--r--  1 root root  141 Oct  9 09:47 inventory_aws_ec2.yaml
    -rw-r--r--  1 root root  842 Oct  9 09:47 jenkins-playbook.yaml
    -r--------  1 root root 3244 Oct  9 09:47 ssh-key.pem
```

Docker installed on the EC2 instance:

```bash
    [ec2-user@ip-172-31-3-123 ~]$ docker --version
    Docker version 25.0.14, build 0bab007
```


 
</details>

******

<details>
<summary>Ansible Roles - Make your Ansible content more reusable and modular</summary>
 <br />

### Demo Executed: Refactor the Docker Playbook to Use Roles

The playbook from the "Run Docker applications" project is refactored: the user creation and the container start parts are moved into two roles (`create_user` and `start_containers`). The servers are 2 EC2 instances created with the same Terraform configuration, and the hosts come from the `aws_ec2` dynamic inventory.

#### What is a Role?
A role packages everything one job needs (tasks, variables, files, templates) into a fixed folder structure. Ansible knows what to look for in each folder, so a playbook only needs the role name. It is similar to a module in Terraform: written once, reused in many playbooks.

#### Role Directory Structure
Each folder is optional; Ansible reads `main.yaml` from the ones that exist.

```bash
    roles/
    └── <role_name>/
        ├── tasks/main.yaml      # the tasks the role runs
        ├── defaults/main.yaml   # default variable values (lowest priority, meant to be overridden)
        ├── vars/main.yaml       # role variables (high priority, not meant to be overridden)
        ├── files/               # static files for copy (no path needed in src)
        ├── templates/           # Jinja2 templates for the template module
        ├── handlers/main.yaml   # handlers triggered with notify
        └── meta/main.yaml       # role metadata and dependencies
```

My project:

```bash
    08-roles/
    ├── ansible.cfg
    ├── inventory_aws_ec2.yaml
    ├── deploy-docker-with-roles.yaml
    ├── project-vars
    └── roles/
        ├── create_user/
        │   ├── defaults/main.yaml
        │   └── tasks/main.yaml
        └── start_containers/
            ├── defaults/main.yaml
            ├── files/docker-compose.yaml
            ├── tasks/main.yaml
            └── vars/main.yaml
```

#### Variable Precedence
The same variable can be defined in many places. When it is defined more than once, the place with the higher priority wins. A simplified order, from lowest to highest:

| Priority | Where the variable is defined |
|---|---|
| 1 (lowest) | Role `defaults/main.yaml` |
| 2 | Inventory (group vars, host vars) |
| 3 | Play `vars:` |
| 4 | Play `vars_files:` |
| 5 | Role `vars/main.yaml` |
| 6 | Task `vars:`, `set_fact`, registered variables |
| 7 (highest) | Extra vars on the command line (`-e "key=value"`) |

* Values that the playbook should be able to change go into `defaults`.
* Values that should stay fixed go into `vars`, because they override even the play variables.
* `-e` always wins, which is useful for a one-time override.

#### Roles
**`create_user`**: the group list comes from a default value, which the playbook overrides.

```yaml
    # roles/create_user/tasks/main.yaml
    - name: Create new user
      user:
        name: dockeruser
        groups: "{{ user_groups }}"
        append: yes

    # roles/create_user/defaults/main.yaml
    user_groups: admin,dockerterr
```

**`start_containers`**: `docker-compose.yaml` is in the role's `files/` folder, so `copy` finds it with only the file name.

```yaml
    # roles/start_containers/tasks/main.yaml
    - name: copy docker compose
      copy:
        src: docker-compose.yaml
        dest: /home/dockeruser/docker-compose.yaml

    - name: Docker login
      docker_login:
        registry_url: "{{ docker_registry }}"
        username: "{{ docker_username }}"
        password: "{{ docker_password }}"

    - name: Start containers
      community.docker.docker_compose_v2:
        project_src: /home/dockeruser
```

The defaults are generic placeholders (an AWS ECR example). `vars/main.yaml` sets the real registry and username for Docker Hub, and overrides the defaults:

```yaml
    # roles/start_containers/defaults/main.yaml
    docker_registry: https://aws_account_id.dkr.ecr.region.amazonaws.com
    docker_username: AWS
    docker_password: 123456

    # roles/start_containers/vars/main.yaml
    docker_registry: https://index.docker.io/v1/
    docker_username: emrearabacioglu
```

#### Playbook
The Docker and Docker Compose installation stay as tasks; the other two plays only call the roles.

```yaml
    ---
    - name: Install Docker
      hosts: all
      become: yes
      tasks:
        - name: Install Docker
          yum:
            name: docker
            update_cache: yes
            state: present

        - name: Start docker daemon
          systemd:
            name: docker
            state: started

    - name: Create new user
      hosts: all
      vars_files: project-vars
      become: yes
      vars:
        user_groups: adm,docker
      roles:
        - create_user

    - name: Install docker-compose
      hosts: all
      become: yes
      become_user: dockeruser
      tasks:
        - name: Create docker-compose directory
          file:
            path: ~/.docker/cli-plugins
            state: directory

        - name: Get arcthitecture of remote machine
          shell: uname -m
          register: remote_arch

        - name: Install docker-compose
          get_url:
            url: "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-{{remote_arch.stdout}}"
            dest: ~/.docker/cli-plugins/docker-compose
            mode: +x

    - name: Start docker containers
      hosts: all
      become: yes
      become_user: dockeruser
      vars_files: project-vars
      roles:
        - start_containers
```

How the variables are resolved in this playbook:

| Variable | Defined in | Used value from |
|---|---|---|
| `user_groups` | role defaults, play `vars` | play `vars` (`adm,docker`) |
| `docker_registry` | role defaults, role vars | role vars (Docker Hub) |
| `docker_username` | role defaults, role vars | role vars |
| `docker_password` | role defaults, `project-vars` | `project-vars` (`vars_files`, the real password) |

#### Execution
Task names from a role are shown with the role name as a prefix (`create_user : ...`).

```bash
    (.venv) root@PC:~/modules/ansible/08-roles (main)# ansible-playbook deploy-docker-with-roles.yaml

    PLAY [Install Docker] ****

    TASK [Gathering Facts] ****
    ok: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    ok: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [Install Docker] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [Start docker daemon] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    PLAY [Create new user] ****

    TASK [Gathering Facts] ****
    ok: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    ok: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [create_user : Create new user] ****
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]

    PLAY [Install docker-compose] ****
    ...
    TASK [Install docker-compose] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    PLAY [Start docker containers] ****

    TASK [Gathering Facts] ****
    ok: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    ok: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [start_containers : copy docker compose] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [start_containers : Docker login] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    TASK [start_containers : Start containers] ****
    changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
    changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

    PLAY RECAP ****
    ec2-3-120-98-66.eu-central-1.compute.amazonaws.com : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ec2-3-72-65-70.eu-central-1.compute.amazonaws.com : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```


 
</details>

******

