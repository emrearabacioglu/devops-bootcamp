# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Structure Playbooks with Ansible Roles

### Demo Executed: Refactor the Docker Playbook to Use Roles

The playbook from the "Ansible & Docker" project is refactored: the user creation and the container start parts are moved into two roles (`create_user` and `start_containers`). The servers are 2 EC2 instances created with the same Terraform configuration, and the hosts come from the `aws_ec2` dynamic inventory.

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
