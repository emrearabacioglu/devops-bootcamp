# Frankfurt (default provider)
provider "aws" {
  region = "eu-central-1"
}

# Paris
provider "aws" {
  alias  = "paris"
  region = "eu-west-3"
}

variable instance_type {}

# AMI IDs are different in every region, so we look them up per region
data "aws_ami" "amazon-linux-image-frankfurt" {
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

data "aws_ami" "amazon-linux-image-paris" {
  provider    = aws.paris
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

# Instances use the default VPC / default subnet of each region (no subnet_id given)
resource "aws_instance" "frankfurt-server-1" {
  ami           = data.aws_ami.amazon-linux-image-frankfurt.id
  instance_type = var.instance_type

  tags = {
    Name = "frankfurt-server-1"
  }
}

resource "aws_instance" "frankfurt-server-2" {
  ami           = data.aws_ami.amazon-linux-image-frankfurt.id
  instance_type = var.instance_type

  tags = {
    Name = "frankfurt-server-2"
  }
}

resource "aws_instance" "paris-server-1" {
  provider      = aws.paris
  ami           = data.aws_ami.amazon-linux-image-paris.id
  instance_type = var.instance_type

  tags = {
    Name = "paris-server-1"
  }
}

output "frankfurt-instance-ids" {
  value = [aws_instance.frankfurt-server-1.id, aws_instance.frankfurt-server-2.id]
}

output "paris-instance-ids" {
  value = [aws_instance.paris-server-1.id]
}