provider "aws" {
  region = "eu-central-1"
}

variable instance_type {}

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

# Instances use the default VPC / default subnet (no subnet_id given)
resource "aws_instance" "prod-server" {
  ami               = data.aws_ami.amazon-linux-image.id
  instance_type     = var.instance_type
  availability_zone = "eu-central-1a"

  tags = {
    Name        = "prod"
    environment = "prod"
  }

  volume_tags = {
    Name        = "prod"
    environment = "prod"
  }
}

resource "aws_instance" "dev-server" {
  ami               = data.aws_ami.amazon-linux-image.id
  instance_type     = var.instance_type
  availability_zone = "eu-central-1a"

  tags = {
    Name        = "dev"
    environment = "dev"
  }

  volume_tags = {
    Name        = "dev"
    environment = "dev"
  }
}

output "prod-server" {
  value = {
    instance_id = aws_instance.prod-server.id
    az          = aws_instance.prod-server.availability_zone
    volume_id   = aws_instance.prod-server.root_block_device[0].volume_id
  }
}

output "dev-server" {
  value = {
    instance_id = aws_instance.dev-server.id
    az          = aws_instance.dev-server.availability_zone
    volume_id   = aws_instance.dev-server.root_block_device[0].volume_id
  }
}