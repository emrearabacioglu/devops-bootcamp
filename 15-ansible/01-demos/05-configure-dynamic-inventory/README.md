# Configure Dynamic Inventory

**Technologies:** Ansible, Terraform, AWS

I replaced the static hosts file with the `aws_ec2` inventory plugin, so Ansible gets the EC2 servers from AWS. Then I configured only the dev servers by using a group that the plugin creates from the Name tag.

## Summary
1. `terraform/main.tf` creates the EC2 instances in the default VPC. I started with 3 servers, then added a 4th one (the next `ansible-inventory` run listed it without editing any file), and in the end tagged them as 2 `dev-server` and 2 `prod-server`. `terraform/terraform.tfvars.example` shows the variables, with `my_ip` masked.
2. `inventory_aws_ec2.yaml` configures the `aws_ec2` plugin (`amazon.aws` collection, uses `boto3`) for `eu-central-1`. `keyed_groups` creates one group per Name tag (`tag_Name_...`) and one per instance type (`instance_type_...`).
3. `ansible.cfg` uses this file as the default inventory, enables the plugin and sets `remote_user = ec2-user` and the private key, so no `-i` or connection options are needed.
4. `deploy-docker-dynamic.yaml` is the playbook from the "Ansible Integration in Terraform" project. Only the target changed: all plays use `hosts: tag_Name_dev_server`, so the prod servers are skipped.
5. The playbook still loads `project-vars` (user groups and my Docker Hub password), which is in `.gitignore` and not in the repo.

## Run
```bash
ansible-inventory -i inventory_aws_ec2.yaml --graph
ansible-playbook deploy-docker-dynamic.yaml
```

## Result
The plugin groups the servers by Name tag, and the playbook runs only on the 2 dev servers:
```
  |--@tag_Name_prod_server:
  |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
  |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
...
  |--@tag_Name_dev_server:
  |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
  |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
...
PLAY RECAP ****
ec2-35-159-49-8.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ec2-63-181-5-198.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
