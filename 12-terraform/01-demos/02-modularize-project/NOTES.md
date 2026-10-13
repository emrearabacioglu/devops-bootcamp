# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Modularize Project

### Demo Executed: Split the configuration into modules

#### Extracted output values, variables and providers into its own file
Moved the outputs to `outputs.tf`, the variables to `variables.tf` and the provider requirements to `providers.tf`:

```bash
    root@PC:~/modules/terraform (feature/modules)# cat outputs.tf
    output "aws_ami_id" {
        value = data.aws_ami.latest-amazon-linux-image.id
    }
    
    output "ec2_public_ip" {
        value = aws_instance.myapp-server.public_ip
    }

    root@PC:~/modules/terraform (feature/modules)# cat providers.tf
    terraform {
      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "~> 6.0"
        }
        linode = {
          source  = "linode/linode"
          version = "4.4.0"
        }
      }
    }

    root@PC:~/modules/terraform (feature/modules)# cat variables.tf
    variable vpc_cidr_block {}
    variable subnet_cidr_block{}
    variable avail_zone {}
    variable env_prefix {}
    variable my_ip{}
    variable instance_type{}
    variable public_key_location{}
```

#### Created subnet module and used it in root config file
Moved the subnet, internet gateway and route table into `modules/subnet`. The root `main.tf` calls the module and passes the variables it needs:

```bash
    root@PC:~/modules/terraform/modules/subnet (feature/modules)# cat main.tf
    resource "aws_subnet" "myapp-subnet-1" {
        vpc_id = var.vpc_id
        cidr_block = var.subnet_cidr_block
        availability_zone = var.avail_zone
        tags = {
            Name: "${var.env_prefix}-subnet-1"
        }
    }
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = var.vpc_id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }
    
    resource "aws_default_route_table" "main-rtb" {
        default_route_table_id = var.default_route_table_id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-main-rtb"
        }
    }

    root@PC:~/modules/terraform (feature/modules)# cat main.tf
    ...
    module "myapp-subnet" {
        source = "./modules/subnet"
        subnet_cidr_block = var.subnet_cidr_block
        avail_zone = var.avail_zone
        env_prefix = var.env_prefix
        vpc_id = aws_vpc.myapp-vpc.id
        default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
    }
    ...
```

#### Created webserver module and used it in root config file
Moved the security group, AMI data source, key pair and EC2 instance into `modules/webserver`. The root config passes the `subnet_id` from the subnet module's output. Fixed two errors on the way: missing `=` signs in block definitions, and the `user_data` path, which now uses `${path.module}`.

```bash
    root@PC:~/modules/terraform/modules/webserver (feature/modules)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = var.subnet_id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        user_data = file("${path.module}/entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }

    root@PC:~/modules/terraform (feature/modules)# cat main.tf
    ...
    module "myapp-server" {
        source = "./modules/webserver"
        vpc_id = aws_vpc.myapp-vpc.id
        my_ip = var.my_ip
        env_prefix = var.env_prefix
        image_name = var.image_name
        public_key_location = var.public_key_location
        instance_type = var.instance_type
        subnet_id = module.myapp-subnet.subnet.id
        avail_zone = var.avail_zone
    }
```

#### terraform init and apply
Ran `terraform init` again to load the modules. The apply destroyed the old root-level resources and created them again inside the modules. Docker was installed on the new server:

```bash
    root@PC:~/modules/terraform (feature/modules)# terraform init
    Initializing the backend...
    
    Initializing modules...
    - myapp-server in modules/webserver
    - myapp-subnet in modules/subnet
    ...
    Terraform has been successfully initialized!

    root@PC:~/modules/terraform (feature/modules)# terraform apply --auto-approve
    ...
    module.myapp-server.aws_instance.myapp-server: Creating...
    module.myapp-server.aws_instance.myapp-server: Creation complete after 13s [id=i-015b96172c33e1907]
    aws_instance.myapp-server: Destruction complete after 20s
    ...
    Apply complete! Resources: 3 added, 0 changed, 2 destroyed.
    
    Outputs:
    ec2_public_ip = "63.183.197.82"

    root@PC:~/modules/terraform (feature/modules)# ssh ec2-user@63.183.197.82
    ...
    [ec2-user@ip-10-0-10-239 ~]$ docker -v
    Docker version 25.0.14, build 0bab007
```
