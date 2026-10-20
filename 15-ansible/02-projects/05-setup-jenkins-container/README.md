# Module 15 – Ansible exercise: Jenkins server on EC2 (Amazon Linux or Ubuntu)

**Technologies:** Ansible (roles, handlers, `aws_ec2` dynamic inventory), AWS (EC2, Security Groups, Key Pairs, SSM Parameter Store), Jenkins, Docker, Node.js, npm, Amazon Linux 2023, Ubuntu 24.04

Ansible code that creates an EC2 server and installs Jenkins on it, with Node.js, npm and Docker available for Jenkins builds. The distro is chosen with `-e os=amazon` or `-e os=ubuntu`, and Jenkins is installed by a single role that picks the right tasks for the server's OS.

## How it works

```
provision.yaml -e os=ubuntu            runs on localhost, talks to the AWS API
  ├─ my public IP        ← checkip.amazonaws.com
  ├─ key pair ansible-key ← ~/.ssh/id_rsa.pub
  ├─ security group <os>-sg: 22 from my IP only, 8080 from anywhere
  └─ EC2 t3.small, AMI read from SSM, tags: Name, OS, Role=jenkins
                     │
                     ▼
inventory_aws_ec2.yaml                 dynamic inventory, no IPs stored anywhere
  ├─ only running instances with Role=jenkins
  ├─ groups from tags: tag_OS_amazon, tag_OS_ubuntu
  └─ ansible_user from the OS tag: ubuntu / ec2-user
                     │
                     ▼
setup-jenkins.yaml [-e os=ubuntu]      hosts: tag_OS_<os>, or tag_OS_* if os is not given
  └─ role jenkins
       ├─ facts → ansible_os_family = RedHat | Debian
       ├─ include RedHat.yaml or Debian.yaml     repo + GPG key + packages
       └─ common tasks: jenkins user → docker group, start docker and jenkins,
                        wait for initialAdminPassword and print it
```

| File                                | What it does                                                                                                                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `os_config.yaml`                  | AWS region and the per-OS values: instance name, SSM parameter for the AMI, security group name. Loaded by`provision.yaml` and `destroy-instance.yaml`. |
| `provision.yaml`                  | Finds the current public IP, imports the SSH key as a key pair, creates the security group and launches the instance.                                       |
| `inventory_aws_ec2.yaml`          | Asks AWS for running Jenkins instances, groups them by the`OS` tag and sets the SSH user per host.                                                        |
| `ansible.cfg`                     | Points to the dynamic inventory and the SSH private key, disables host key checking.                                                                        |
| `setup-jenkins.yaml`              | Runs the`jenkins` role on one OS group or on all Jenkins servers.                                                                                         |
| `roles/jenkins/tasks/main.yml`    | Includes the OS-specific file, then runs the tasks that are the same on both distros.                                                                       |
| `roles/jenkins/tasks/RedHat.yaml` | Amazon Linux: Jenkins RPM repo and GPG key, then`dnf` installs Corretto 21, fontconfig, Jenkins, Docker, Node.js and npm.                                 |
| `roles/jenkins/tasks/Debian.yaml` | Ubuntu: Jenkins key in`/etc/apt/keyrings`, apt repo with `signed-by`, OpenJDK 21 first, then Jenkins, `docker.io`, Node.js and npm.                   |
| `roles/jenkins/handlers/main.yml` | Restarts Jenkins when the jenkins user is added to the docker group.                                                                                        |
| `destroy-instance.yaml`           | Terminates the instance, then deletes its security group and the key pair.                                                                                  |

### Decisions

- **No duplicate servers on re-run.** `ec2_instance` uses `exact_count: 1` with explicit `filters` on the `Name` tag and the instance state. The module's default filter also compares the AMI ID, so a newer AMI in SSM would launch a second server.
- **No hardcoded AMI.** The AMI ID is read at runtime from AWS's public SSM parameters, so it is always the latest image for the region.
- **No saved IPs.** The setup playbook finds the servers through the dynamic inventory by their tags, so a changed IP doesn't break anything.
- **Tools installed system-wide.** Node.js and npm come from the distro repos (not nvm), so they are in `/usr/bin` and visible to the jenkins user in pipeline `sh` steps.
- **Destroy is written by hand.** Ansible keeps no state like Terraform, so `destroy-instance.yaml` deletes what `provision.yaml` created, in reverse order. The security group can only be deleted after the instance is terminated.

## Requirements

- Ansible with the `amazon.aws` collection, and `boto3` / `botocore` in the same Python environment
- AWS credentials in `~/.aws/credentials` with EC2 and SSM read permissions
- SSH key pair at `/root/.ssh/id_rsa` and `/root/.ssh/id_rsa.pub`

## Usage

All commands run in this folder.

```bash
# 1. Create the server (os is required: amazon or ubuntu)
ansible-playbook provision.yaml -e os=ubuntu
ansible-playbook provision.yaml -e os=amazon

# 2. Check that the inventory finds the servers and SSH works
ansible-inventory --graph
ansible all -m ping

# 3. Install Jenkins
ansible-playbook setup-jenkins.yaml -e os=ubuntu   # only the Ubuntu server
ansible-playbook setup-jenkins.yaml                # every Jenkins server

# 4. Delete the server, its security group and the key pair
ansible-playbook destroy-instance.yaml -e os=ubuntu
```

The initial admin password is printed at the end of step 3. Jenkins is then at `http://<public-ip>:8080`.

Check that the jenkins user can use the build tools:

```bash
ansible all -b --become-user jenkins -m command -a "docker ps"
ansible all -b --become-user jenkins -m command -a "npm -v"
```
