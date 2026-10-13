# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Ansible & Docker

### Demo Executed: Install Docker and Docker Compose and Start the Containers with Ansible

#### Preparation
* Created an EC2 instance (Amazon Linux 2023) with Terraform in the default VPC. The security group allows SSH from my IP and port `8080` for the application.
* Built the Java application image and pushed it to a private Docker Hub repository (`emrearabacioglu/java-mysql-app:1.0`).

#### Playbook
* **Install Docker** – installs Docker with the `yum` module and starts the Docker daemon with `systemd`.
* **Create new user** – creates `dockeruser` and adds it to the `docker` group, so the containers don't run with the default `ec2-user`.
* **Install docker-compose** – runs as `dockeruser`. Docker Compose is not in the Amazon Linux repository, so the Compose plugin is downloaded from the GitHub releases to `~/.docker/cli-plugins`. The download URL needs the CPU architecture of the server, which comes from `uname -m`.
* **Start docker containers** – copies the compose file to the server, logs in to Docker Hub with `docker_login` (the password comes from the variables file) and starts the containers with `docker_compose_v2`.

`deploy-docker.yaml`:

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
The three containers are running:

```bash
    [ec2-user@ip-172-31-40-163 ~]$ sudo docker ps
    CONTAINER ID   IMAGE                                COMMAND                  CREATED              STATUS              PORTS                                                  NAMES
    00062373a8fc   emrearabacioglu/java-mysql-app:1.0   "/__cacert_entrypoin…"   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp              my-java-app
    2a847c1ca772   phpmyadmin                           "/docker-entrypoint.…"   About a minute ago   Up About a minute   0.0.0.0:8083->80/tcp, :::8083->80/tcp                  myadmin
    e05688155b87   mysql                                "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql
```
