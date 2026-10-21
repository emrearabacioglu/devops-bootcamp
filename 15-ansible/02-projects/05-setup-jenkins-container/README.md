# Jenkins as a Docker container on EC2 (Amazon Linux or Ubuntu)

**Technologies:** Ansible (roles, `aws_ec2` dynamic inventory, `community.docker`), Docker, Jenkins, Node.js, npm, AWS (EC2, Security Groups, Key Pairs, SSM Parameter Store), Amazon Linux 2023, Ubuntu 24.04

Ansible code that creates an EC2 server (Amazon Linux 2023 or Ubuntu 24.04) and runs Jenkins on it as a Docker container, with Node.js, npm and Docker available for Jenkins builds. The distro is chosen with `-e os=amazon` or `-e os=ubuntu`. One playbook creates the server, another installs Docker and starts Jenkins, a third deletes everything.

The host only gets Docker. Everything Jenkins needs for builds (docker CLI, Node.js, npm) is baked into a custom image built from `jenkins/jenkins:lts`, so the inside of the container is the same on both distros.

## How it works

```
provision.yaml -e os=ubuntu        EC2 + security group + key pair, tags Name, OS, Role=jenkins
                  │
                  ▼
inventory_aws_ec2.yaml             groups tag_OS_amazon / tag_OS_ubuntu, SSH user from the OS tag
                  │
                  ▼
setup-jenkins.yaml [-e os=...]     role jenkins on one OS group or on all Jenkins servers
  ├─ RedHat.yaml / Debian.yaml     install Docker (docker / docker.io) + python3-requests
  ├─ start and enable docker
  ├─ getent group docker           host's docker GID, e.g. 993 on Amazon Linux, 113 on Ubuntu
  ├─ copy files/Dockerfile → /opt/jenkins/
  ├─ build image custom-jenkins    jenkins/jenkins:lts + nodejs, npm, docker CLI
  ├─ run container jenkins
  │    ports   8080, 50000
  │    volume  jenkins_home → /var/jenkins_home
  │    socket  /var/run/docker.sock → /var/run/docker.sock
  │    groups  <host docker GID>
  └─ wait for initialAdminPassword in the volume on the host and print it
```

| File                                                                                                           | What it does                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `provision.yaml`, `destroy-instance.yaml`, `os_config.yaml`, `inventory_aws_ec2.yaml`, `ansible.cfg` | Create and delete the server, its security group and the key pair. The per-OS values (AMI, names) are in `os_config.yaml`. The dynamic inventory finds the servers by tags and sets the SSH user per OS. |
| `setup-jenkins.yaml`                                                                                         | Runs the `jenkins` role on `tag_OS_<os>`, or on every Jenkins server when `os` is not given.                                            |
| `roles/jenkins/tasks/RedHat.yaml`                                                                            | Amazon Linux: installs `docker` and `python3-requests` with dnf.                                                                          |
| `roles/jenkins/tasks/Debian.yaml`                                                                            | Ubuntu: installs `docker.io` and `python3-requests` with apt.                                                                             |
| `roles/jenkins/tasks/main.yml`                                                                               | Includes the OS file, then everything else: Docker service, docker GID, image build, container, password.                                    |
| `roles/jenkins/files/Dockerfile`                                                                             | Custom image: `jenkins/jenkins:lts` plus `nodejs`, `npm` and `docker.io` (only its CLI is used), back to `USER jenkins` at the end. |
| `test-all.sh`, `test.log`                                                                                  | Full test run on both distros and its output.                                                                                                |

### Decisions

- **Custom image instead of installing tools into a running container.** The tools are part of the image, so a recreated container has them right away. Nothing is changed by hand inside the container.
- **Docker from the host.** The container mounts the host's `/var/run/docker.sock`. The docker CLI inside the container talks to the host's Docker daemon, so images built by Jenkins land on the host.
- **Socket permission with the numeric GID.** The socket belongs to the host's `docker` group. The jenkins user in the container is not in that group, so the container gets the host's docker GID through `groups`. It must be the number, not the name: a group name would be looked up in the container's own `/etc/group`, while the kernel checks the number. The GID differs per distro (993 on Amazon Linux, 113 on Ubuntu in the test run), so it is read with `getent` on each host instead of being hardcoded.
- **Named volume for Jenkins data.** Jobs, plugins and settings live in the `jenkins_home` volume and survive a recreated container. The volume sits on the host at `/var/lib/docker/volumes/jenkins_home/_data`, so the initial admin password is read from there with `wait_for` + `slurp`.
- **Rebuild on Dockerfile changes.** `force_source: true` builds every run. With an unchanged Dockerfile the build cache gives the same image ID and the container is left alone. With a changed Dockerfile the image ID changes and `docker_container` recreates the container from the new image. The data stays in the volume.
- **`restart_policy: unless-stopped`.** The container comes back after a reboot.
- **No duplicate servers on re-run.** `ec2_instance` uses `exact_count: 1` with explicit `filters` on the `Name` and `OS` tags and the instance state. The AMI ID is read at runtime from AWS's public SSM parameters, so it is never hardcoded.
- **Destroy is written by hand.** Ansible keeps no state, so `destroy-instance.yaml` deletes what `provision.yaml` created, in reverse order: instance, security group, key pair.

## Requirements

- Ansible with the `amazon.aws` and `community.docker` collections, and `boto3` / `botocore` in the same Python environment
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

# 3. Install Docker and start the Jenkins container
ansible-playbook setup-jenkins.yaml -e os=ubuntu   # only the Ubuntu server
ansible-playbook setup-jenkins.yaml                # every Jenkins server

# 4. Delete the server, its security group and the key pair
ansible-playbook destroy-instance.yaml -e os=ubuntu
```

The initial admin password is printed at the end of step 3. Jenkins is then at `http://<public-ip>:8080`.

Check that the build tools work inside the container, as the jenkins user:

```bash
ansible all -b -m command -a "docker exec jenkins docker ps"
ansible all -b -m command -a "docker exec jenkins npm -v"
```

## Testing

`test-all.sh` runs the whole flow on both distros and stops at the first error: syntax check, provision Ubuntu and Amazon Linux, wait for SSH, install Jenkins, run the setup a second time, check that Jenkins answers on port 8080, then run `id`, `docker ps`, `node -v` and `npm -v` inside each container. The servers are left running so Jenkins can be opened in the browser.

```bash
bash test-all.sh 2>&1 | tee test.log
```

Results from [`test.log`](./test.log):

- Both servers provisioned and reachable over SSH, each with its own SSH user from the inventory.
- First setup run installed everything. The second run ended with `changed=0` on both hosts.
- Jenkins 2.580.1 answered `200` on `/login` on both servers.
- Inside the containers the jenkins user had the host's docker GID as an extra group (`993` on Amazon Linux, `113` on Ubuntu), and `docker ps` listed the host's containers.
- Node.js `v20.19.2` and npm `9.2.0` in both containers.
