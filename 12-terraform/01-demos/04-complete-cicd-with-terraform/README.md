# Complete CI/CD with Terraform / Configure a Shared Remote State

**Technologies:** Terraform, Jenkins, Docker, AWS, AWS S3, Git, Java, Maven, Linux, Docker Hub

Instead of deploying to an existing server, my Jenkins pipeline now creates the EC2 server with Terraform and then deploys the app to it with Docker Compose. After that I moved the Terraform state to an S3 bucket, so Jenkins and my local machine use the same state.

## Summary
1. Created the `myapp-key-pair` key pair in AWS. Added the credentials in Jenkins: AWS access keys (`jenkins_aws_access_key_id`, `jenkins_aws_access_secret_key`), Docker Hub login (`docker-hub-repo`) and the EC2 SSH key (`server-ssh-key`).
2. Installed Terraform inside the Jenkins container.
3. Added `java-maven-app/terraform/` to the app repo: `main.tf` creates a VPC, subnet, Internet Gateway, default route table, security group (SSH from my IP and the Jenkins server IP) and a `t2.micro` instance. `variables.tf` has the defaults. `entry-script.sh` runs as user data and installs Docker and Docker Compose.
4. `java-maven-app/Jenkinsfile` (uses my Jenkins shared library) has these stages:
   - **build app** (CI): builds the jar with Maven
   - **build image** (CI): builds the Docker image and pushes it to Docker Hub
   - **provision server** (CD): `terraform init` + `terraform apply`, then reads the IP with `terraform output -raw ec2_public_ip`
   - **deploy** (CD): waits 90 seconds for the server, copies `server-cmds.sh` and `docker-compose.yaml` with `scp` and runs `server-cmds.sh` over SSH. The script logs in to Docker Hub and starts the app and `postgres:16` with Docker Compose.

## Configure a Shared Remote State
1. Destroyed the existing infrastructure from inside the Jenkins container first, so the old local state would not conflict with the new backend.
2. Created the S3 bucket `myapp-tf-s3-bucket-3673` and added a `backend "s3"` block to `terraform/main.tf` (key `myapp/state.tfstate`).
3. Ran the pipeline again: `terraform init` configured the S3 backend, the apply created the server and the app was deployed.
4. Ran `terraform init` locally in the same folder. It connected to the same bucket and `terraform state list` showed the resources Jenkins had created.

## Result
Pipeline run with the S3 backend (Jenkins console log):
```
+ terraform init
Initializing the backend...

Successfully configured the backend "s3"! Terraform will automatically
...
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
...
Container ec2-user-postgres-1 Started
success
...
Finished: SUCCESS
```
The same state read from my machine:
```
root@PC:~/modules/terraform/java-terraform/terraform (master)# terraform state list
data.aws_ami.latest-amazon-linux-image
aws_default_route_table.main-rtb
aws_default_security_group.default-sg
aws_instance.myapp-server
aws_internet_gateway.myapp-igw
aws_subnet.myapp-subnet-1
aws_vpc.myapp-vpc
```

Commit history: my [java-terraform](https://github.com/emrearabacioglu/java-terraform) repo.

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
