terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      environment = var.env_prefix
      application = "myapp"
      managed-by  = "terraform"
    }
  }
}
