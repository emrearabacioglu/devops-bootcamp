# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Ansible Integration in Terraform

### Demo Executed: Run the Ansible Playbook Automatically after Terraform Creates the Servers

#### Terraform Configuration
The servers from the previous project are now configured automatically. Once Terraform creates the EC2 instances, it runs the Ansible playbook:

* `count = 2` creates two instances in the default VPC.
* A `null_resource` with a `local-exec` provisioner runs `ansible-playbook` on my machine. `working_dir` points to the parent folder where the playbook and the Ansible files are.
* The public IPs of all instances are passed with `join()` directly as the inventory (the trailing comma tells Ansible it is a host list, not a file). The SSH key and the user are given on the command line.
* `triggers` uses the same IP list, so the playbook runs again when the instances change.

The Terraform configuration:

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

Beginning of the updated playbook:

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
Containers running on one of the new servers:

```bash
    [ec2-user@ip-172-31-34-32 ~]$ sudo docker ps
    CONTAINER ID   IMAGE                                COMMAND                  CREATED          STATUS          PORTS                                                  NAMES
    f88e6b63e99b   emrearabacioglu/java-mysql-app:1.0   "/__cacert_entrypoin…"   16 seconds ago   Up 2 seconds    0.0.0.0:8080->8080/tcp, :::8080->8080/tcp              my-java-app
    e42c069e3c23   mysql                                "docker-entrypoint.s…"   16 seconds ago   Up 14 seconds   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql
    56f3daa09d35   phpmyadmin                           "/docker-entrypoint.…"   16 seconds ago   Up 14 seconds   0.0.0.0:8083->80/tcp, :::8083->80/tcp                  myadmin
```
