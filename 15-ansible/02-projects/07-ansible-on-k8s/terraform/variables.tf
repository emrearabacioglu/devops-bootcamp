variable "vpc_cidr_block" {}
variable "private_subnet_cidr_blocks" {}
variable "public_subnet_cidr_blocks" {}

variable "env_prefix" {}

locals {
  cluster_name = "${var.env_prefix}-myapp-eks-cluster"
}