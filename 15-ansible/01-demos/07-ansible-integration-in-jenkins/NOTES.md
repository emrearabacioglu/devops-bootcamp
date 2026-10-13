# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Ansible Integration in Jenkins

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

`Jenkinsfile`:

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
Console output of the pipeline run:

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
