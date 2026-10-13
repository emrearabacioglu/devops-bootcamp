# Automate AWS Infrastructure

**Technologies:** Terraform, AWS, Docker, Linux, Git

I wrote a Terraform config that creates the network parts and an EC2 instance on AWS, and starts an nginx Docker container on the instance.

## Summary
- `main.tf` creates a VPC, a subnet and an Internet Gateway, and adds a `0.0.0.0/0` route to the VPC's default route table (`aws_default_route_table`). I first used a custom route table with a subnet association, then switched to the default one.
- The default security group (`aws_default_security_group`) allows SSH (22) only from my IP and port 8080 from everywhere.
- The AMI comes from a `data "aws_ami"` block (latest Amazon Linux 2023). `aws_key_pair` uploads my local public key, so I don't need a key pair created in the AWS console.
- The EC2 instance runs `entry-script.sh` as `user_data`: it installs and starts Docker, adds `ec2-user` to the docker group and runs nginx on port 8080.
- `providers.tf` has the provider versions. Values come from `terraform.tfvars` (not in git). `terraform.tfvars.example` shows the variables, the values there are only examples.
- `with-provisioners/` is the same setup from the "Provisioners" lesson: the `file` provisioner copies `entry-script.sh` to the server, `remote-exec` runs it and `local-exec` writes the public IP to `output.txt` on my machine. It also needs `private_key_location` for the SSH `connection` block. Terraform recommends `user_data` over provisioners, so the main version uses `user_data`.

## Run
```bash
terraform init
terraform plan
terraform apply --auto-approve
ssh ec2-user@<public-ip>
terraform destroy
```

## Result
Apply with `entry-script.sh` as user data, then the nginx container running on the new instance:
```
root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
...
Apply complete! Resources: 1 added, 0 changed, 1 destroyed.

Outputs:
ec2_public_ip = "3.79.21.47"
...
root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@3.79.21.47
...
[ec2-user@ip-10-0-10-134 ~]$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                   NAMES
a25a61191afb   nginx     "/docker-entrypoint.…"   39 seconds ago   Up 37 seconds   0.0.0.0:8080->80/tcp, :::8080->80/tcp   pedantic_wiles
```

Commit history: branches `feature/EC2` and `feature/provisioners` in my [terraform](https://github.com/emrearabacioglu/terraform) repo.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
