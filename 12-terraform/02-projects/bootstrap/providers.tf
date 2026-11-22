terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  # Same bucket as the environments, own key and no workspaces:
  # this project runs once per account, not once per environment.
  backend "s3" {
    bucket       = "emre-myapp-tfstate-10"
    key          = "bootstrap/github-oidc.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      application = "myapp"
      managed-by  = "terraform"
      component   = "github-actions-oidc"
    }
  }
}
