variable "vpc_cidr_block" {}
variable "private_subnet_cidr_blocks" {}
variable "public_subnet_cidr_blocks" {}
variable "mysql_root_password" {
  type      = string
  sensitive = true
}

variable "env_prefix" {}

locals {
  cluster_name = "${var.env_prefix}-myapp-eks-cluster"
}