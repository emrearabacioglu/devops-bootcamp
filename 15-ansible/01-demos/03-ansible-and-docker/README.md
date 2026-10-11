# Ansible & Docker

**Technologies:** Ansible, AWS, Docker, Terraform, Linux

I created an EC2 instance with Terraform and wrote an Ansible playbook that installs Docker and Docker Compose on it, copies `docker-compose.yaml` to the server and starts the containers.

## Summary
1. `terraform/` creates one EC2 instance (Amazon Linux 2023) in the default VPC. The security group allows SSH from my IP and port `8080` for the app. `terraform/terraform.tfvars.example` shows the variables, with `my_ip` masked.
2. Built the Java app image and pushed it to my private Docker Hub repo (`emrearabacioglu/java-mysql-app:1.0`). `docker-compose.yaml` runs it together with `mysql` and `phpmyadmin`.
3. Added the server IP to `hosts` in the group `docker_server` (user `ec2-user`). `ansible.cfg` uses `hosts` as the inventory.
4. `deploy-docker.yaml` has four plays:
   - **Install Docker**: installs Docker with `yum` and starts it with `systemd`.
   - **Create new user**: creates `dockeruser` and adds it to the `docker` group, so the containers don't run with `ec2-user`.
   - **Install docker-compose**: as `dockeruser`, downloads the Compose plugin from the GitHub releases to `~/.docker/cli-plugins`. Compose is not in the Amazon Linux repo, and the download URL needs the CPU architecture from `uname -m`.
   - **Start docker containers**: copies `docker-compose.yaml`, logs in to Docker Hub with `docker_login` and starts the containers with `community.docker.docker_compose_v2`.
5. The plays load `project-vars` with `vars_files` (`user_groups` and `docker_password`). It holds my real Docker Hub password, so it is in `.gitignore` and not in the repo.

## Run
```bash
ansible-playbook deploy-docker.yaml
```

## Result
The playbook ran on a new server and the three containers are running:
```
PLAY RECAP ****
3.73.116.21                : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

[ec2-user@ip-172-31-40-163 ~]$ sudo docker ps
CONTAINER ID   IMAGE                                COMMAND                  CREATED              STATUS              PORTS                                                  NAMES
00062373a8fc   emrearabacioglu/java-mysql-app:1.0   "/__cacert_entrypoin…"   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp              my-java-app
2a847c1ca772   phpmyadmin                           "/docker-entrypoint.…"   About a minute ago   Up About a minute   0.0.0.0:8083->80/tcp, :::8083->80/tcp                  myadmin
e05688155b87   mysql                                "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
