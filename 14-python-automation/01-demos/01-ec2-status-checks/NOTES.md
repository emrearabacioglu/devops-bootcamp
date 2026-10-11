# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Health Check: EC2 Status Checks

### Demo Executed: EC2 Status Checks with Boto3 and a Scheduled Task

#### Preparation: 3 EC2 Instances with Terraform
Reused the AWS infrastructure from the Terraform module (VPC, subnet, security group, internet gateway, route table, key pair) and created 3 EC2 instances to monitor.

```hcl
    provider "aws" {
        region = "eu-central-1"
    }

    variable vpc_cidr_block {}
    variable subnet_cidr_block {}
    variable avail_zone {}
    variable env_prefix {}
    variable instance_type {}
    variable my_ip {}
    variable public_key_location {}

    data "aws_ami" "amazon-linux-image" {
      most_recent = true
      owners      = ["amazon"]

      filter {
        name   = "name"
        values = ["al2023-ami-2023.*-x86_64"]
      }

      filter {
        name   = "virtualization-type"
        values = ["hvm"]
      }
    }

    output "ami_id" {
      value = data.aws_ami.amazon-linux-image.id
    }

    resource "aws_vpc" "myapp-vpc" {
      cidr_block = var.vpc_cidr_block
      tags = {
        Name = "${var.env_prefix}-vpc"
      }
    }

    resource "aws_subnet" "myapp-subnet-1" {
      vpc_id            = aws_vpc.myapp-vpc.id
      cidr_block        = var.subnet_cidr_block
      availability_zone = var.avail_zone
      tags = {
        Name = "${var.env_prefix}-subnet-1"
      }
    }

    resource "aws_security_group" "myapp-sg" {
      name   = "myapp-sg"
      vpc_id = aws_vpc.myapp-vpc.id

      ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = [var.my_ip]
      }

      ingress {
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }

      egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
        prefix_list_ids = []
      }

      tags = {
        Name = "${var.env_prefix}-sg"
      }
    }

    resource "aws_internet_gateway" "myapp-igw" {
      vpc_id = aws_vpc.myapp-vpc.id

      tags = {
        Name = "${var.env_prefix}-internet-gateway"
      }
    }

    resource "aws_route_table" "myapp-route-table" {
      vpc_id = aws_vpc.myapp-vpc.id

      route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.myapp-igw.id
      }

      # default route, mapping VPC CIDR block to "local", created implicitly and cannot be specified.

      tags = {
        Name = "${var.env_prefix}-route-table"
      }
    }

    # Associate subnet with Route Table
    resource "aws_route_table_association" "a-rtb-subnet" {
      subnet_id      = aws_subnet.myapp-subnet-1.id
      route_table_id = aws_route_table.myapp-route-table.id
    }

    resource "aws_key_pair" "ssh-key" {
      key_name   = "myapp-key"
      public_key = file(var.public_key_location)
    }

    output "server-ip" {
      value = aws_instance.myapp-server.public_ip
    }

    resource "aws_instance" "myapp-server" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }

    resource "aws_instance" "myapp-server-two" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server-two"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }

    resource "aws_instance" "myapp-server-three" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server-three"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }
```

Provisioned the instances:
```bash
    root@PC:~/modules/python-automation/01-ec2-health-check/terraform# terraform apply
    ...
    aws_instance.myapp-server-two: Refreshing state... [id=i-0957da2371a8ba1fc]
    aws_instance.myapp-server: Refreshing state... [id=i-0d9ab4ceff4be7078]
    ...
      # aws_instance.myapp-server-three will be created
      + resource "aws_instance" "myapp-server-three" {
          + ami                                  = "ami-0149e5f1dd5234430"
          + instance_type                        = "t3.micro"
          + tags                                 = {
              + "Name" = "dev-server-three"
            }
          ...
        }

    Plan: 1 to add, 0 to change, 0 to destroy.
    ...
    aws_instance.myapp-server-three: Creating...
    aws_instance.myapp-server-three: Creation complete after 15s [id=i-05ec8658146509a8d]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

#### Health Check Script with a Scheduler
`describe_instance_status()` returns the state (running, stopped, terminated…) and the two AWS status checks of each instance:

* **Instance status** – checks the instance itself (OS, network config)
* **System status** – checks the AWS hardware the instance runs on

`IncludeAllInstances=True` also returns instances that are not running; without it only running instances are listed. The `schedule` package runs the check every 5 seconds.

```python
    import boto3
    import schedule

    ec2_client = boto3.client('ec2', region_name="eu-central-1")
    ec2_resource = boto3.resource('ec2', region_name="eu-central-1")


    def check_instance_status():
        statuses = ec2_client.describe_instance_status(
            IncludeAllInstances=True
        )
        for status in statuses['InstanceStatuses']:
            ins_status = status['InstanceStatus']['Status']
            sys_status = status['SystemStatus']['Status']
            state = status['InstanceState']['Name']
            print(f"Instance {status['InstanceId']} is {state}. Instance status: {ins_status}, System status: {sys_status}")
        print("\n")

    schedule.every(5).seconds.do(check_instance_status)

    while True:
        schedule.run_pending()
```

#### Execution
All 3 instances running and healthy (`i-02155…` is an instance replaced earlier by Terraform, it is still listed as `terminated` because of `IncludeAllInstances=True`):
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/01-ec2-health-check/healthcheck.py
    Instance i-0957da2371a8ba1fc is running. Instance status: ok, System status: ok
    Instance i-05ec8658146509a8d is running. Instance status: ok, System status: ok
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
```

While the script was running, removed 2 instances with Terraform:
```bash
    root@PC:~/modules/python-automation/01-ec2-health-check/terraform# terraform apply --auto-approve
    ...
      # aws_instance.myapp-server-three will be destroyed
      # (because aws_instance.myapp-server-three is not in configuration)
    ...
      # aws_instance.myapp-server-two will be destroyed
      # (because aws_instance.myapp-server-two is not in configuration)
    ...
    Plan: 0 to add, 0 to change, 2 to destroy.
    aws_instance.myapp-server-three: Destroying... [id=i-05ec8658146509a8d]
    aws_instance.myapp-server-two: Destroying... [id=i-0957da2371a8ba1fc]
    aws_instance.myapp-server-three: Destruction complete after 31s
    aws_instance.myapp-server-two: Destruction complete after 31s

    Apply complete! Resources: 0 added, 0 changed, 2 destroyed.
```

The scheduled script picked up the state change on its next runs (`running` → `shutting-down` → `terminated`):
```bash
    Instance i-0957da2371a8ba1fc is running. Instance status: ok, System status: ok
    Instance i-05ec8658146509a8d is running. Instance status: ok, System status: ok
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable


    Instance i-0957da2371a8ba1fc is shutting-down. Instance status: not-applicable, System status: not-applicable
    Instance i-05ec8658146509a8d is shutting-down. Instance status: not-applicable, System status: not-applicable
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
    ...

    Instance i-0957da2371a8ba1fc is terminated. Instance status: not-applicable, System status: not-applicable
    Instance i-05ec8658146509a8d is terminated. Instance status: not-applicable, System status: not-applicable
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
```
