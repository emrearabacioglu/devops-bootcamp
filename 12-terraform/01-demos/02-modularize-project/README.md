# Modularize Project

**Technologies:** Terraform, AWS, Docker, Linux, Git

I split the Terraform config from `01-automate-aws-infrastructure` into two modules and called them from the root config.

## Summary
- Moved outputs, variables and provider requirements into their own files: `outputs.tf`, `variables.tf`, `providers.tf`.
- `modules/subnet/` has the subnet, Internet Gateway and default route table. `modules/subnet/outputs.tf` returns the subnet object.
- `modules/webserver/` has the default security group, the AMI lookup (name filter from `image_name`), the key pair and the EC2 instance. `user_data` loads `entry-script.sh` with `${path.module}`, so the path works from inside the module.
- Root `main.tf` creates the VPC and calls both modules. The webserver module gets `subnet_id = module.myapp-subnet.subnet.id`, and root `outputs.tf` prints the public IP from `module.myapp-server.instance`.
- On the way I fixed two errors: missing `=` signs in block definitions, and the `user_data` path.
- Values come from `terraform.tfvars` (not in git). `terraform.tfvars.example` shows the variables, the values there are only examples.

## Run
```bash
terraform init      # needed again after adding modules
terraform apply --auto-approve
```

## Result
`terraform init` loads both modules, the apply recreates the resources inside the modules, and Docker is installed on the new server:
```
root@PC:~/modules/terraform (feature/modules)# terraform init
...
Initializing modules...
- myapp-server in modules/webserver
- myapp-subnet in modules/subnet
...
Apply complete! Resources: 3 added, 0 changed, 2 destroyed.

Outputs:
ec2_public_ip = "63.183.197.82"
...
[ec2-user@ip-10-0-10-239 ~]$ docker -v
Docker version 25.0.14, build 0bab007
```

Commit history: branch `feature/modules` in my [terraform](https://github.com/emrearabacioglu/terraform) repo.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
