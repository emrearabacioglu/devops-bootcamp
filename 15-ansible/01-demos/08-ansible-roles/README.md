# Structure Playbooks with Ansible Roles

**Technologies:** Ansible, Docker, AWS, Linux

I split the Docker playbook from the "Ansible & Docker" project into two roles, `create_user` and `start_containers`, and ran it on 2 EC2 instances from the `aws_ec2` dynamic inventory.

## Summary
1. `terraform/` creates the 2 EC2 instances (`my_ip` masked in `terraform/terraform.tfvars.example`). `inventory_aws_ec2.yaml` and `ansible.cfg` set the dynamic inventory, the SSH user and the key.
2. `roles/create_user/`: `tasks/main.yaml` creates `dockeruser` with the groups from `user_groups`. `defaults/main.yaml` has a default value, which the playbook overrides with `user_groups: adm,docker` in the play `vars`.
3. `roles/start_containers/`: `tasks/main.yaml` copies the compose file, logs in with `docker_login` and starts the containers with `docker_compose_v2`. `docker-compose.yaml` is in the role's `files/` folder, so `copy` finds it by name. `defaults/main.yaml` has placeholder values (an ECR example) and `vars/main.yaml` sets the Docker Hub registry and my username.
4. `deploy-docker-with-roles.yaml`: the Docker and Docker Compose install stay as tasks, the other two plays only call the roles. `docker_password` comes from `project-vars` (`vars_files`), which holds my real password and is in `.gitignore`, so it is not in the repo.
5. Variable precedence: role `defaults` have the lowest priority, so the play `vars` and `vars_files` override them. Role `vars/main.yaml` is higher than play variables, so the registry and username stay fixed.

## Run
```bash
ansible-playbook deploy-docker-with-roles.yaml
```

## Result
Role tasks are shown with the role name as a prefix, and both servers are configured:
```
TASK [create_user : Create new user] ****
changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]
changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
...
TASK [start_containers : Start containers] ****
changed: [ec2-3-72-65-70.eu-central-1.compute.amazonaws.com]
changed: [ec2-3-120-98-66.eu-central-1.compute.amazonaws.com]

PLAY RECAP ****
ec2-3-120-98-66.eu-central-1.compute.amazonaws.com : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ec2-3-72-65-70.eu-central-1.compute.amazonaws.com : ok=13   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
