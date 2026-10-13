# Ansible Integration in Terraform

**Technologies:** Ansible, Terraform, AWS, Docker, Linux

I changed the Terraform configuration so that after it creates the EC2 instances it runs the Ansible playbook from the "Ansible & Docker" project. One `terraform apply` creates and configures the servers.

## Summary
1. `terraform/main.tf` creates 2 EC2 instances (`count = 2`) in the default VPC, with the same security group as before.
2. A `null_resource` with a `local-exec` provisioner runs `ansible-playbook` on my machine from the parent folder (`working_dir`). The public IPs of the instances are joined into the `--inventory` list (the trailing comma tells Ansible it is a host list), and the private key and `ec2-user` are given on the command line. `triggers` uses the same IP list, so the playbook runs again when the instances change.
3. `deploy-docker.yaml` is the playbook from the previous project with two changes: all plays use `hosts: all` (the inventory from Terraform has no groups), and a new first play **Wait SSH connection** waits with `wait_for` until port 22 of each server answers. It runs locally (`ansible_connection: local`), because a new instance is "running" before SSH is ready.
4. `docker-compose.yaml` is the same as before. `project-vars` (user groups and my Docker Hub password) is in `.gitignore`, so it is not in the repo.
5. `terraform/terraform.tfvars.example` shows the variables (incl. `ssh_key_private`), with `my_ip` masked.

## Run
```bash
cd terraform
terraform apply --auto-approve
```

## Result
Terraform creates the servers, runs the playbook on both of them and prints the IPs:
```
null_resource.configure_server (local-exec): Executing: ["/bin/sh" "-c" "ansible-playbook --inventory 18.185.112.89,63.177.48.188, --private-key /root/.ssh/id_rsa --user ec2-user deploy-docker.yaml"]
...
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

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
