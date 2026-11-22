variable "vpc_cidr_block" {}
variable "private_subnet_cidr_blocks" {}
variable "public_subnet_cidr_blocks" {}
variable "mysql_root_password" {
  type      = string
  sensitive = true
}

variable "env_prefix" {}

# --- GitHub Actions + Argo CD version (off by default, so the Jenkins version is unchanged) ---

variable "gitops_enabled" {
  description = "Install Argo CD and External Secrets and give the GitHub Actions plan role read access. Set by the GitHub Actions workflow."
  type        = bool
  default     = false
}

variable "gitops_repo_url" {
  description = "Git repository Argo CD watches."
  type        = string
  default     = "https://github.com/emrearabacioglu/devops-bootcamp.git"
}

variable "gitops_revision" {
  description = "Branch Argo CD follows."
  type        = string
  default     = "main"
}

variable "gha_plan_role_name" {
  description = "IAM role of the plan job (from ../bootstrap). Gets read-only access to the cluster so plans can refresh the Helm releases."
  type        = string
  default     = "gha-terraform-plan"
}

variable "cluster_admin_arns" {
  description = "IAM principals with cluster admin access, e.g. your own IAM user for kubectl. The identity that runs apply is always admin."
  type        = list(string)
  default     = []
}

data "aws_caller_identity" "current" {}

locals {
  cluster_name = "${var.env_prefix}-myapp-eks-cluster"

  admin_access_entries = {
    for arn in var.cluster_admin_arns : arn => {
      principal_arn = arn
      policy_associations = {
        admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
  }

  # AdminView (not View) because Helm keeps its release data in Secrets.
  plan_access_entry = var.gitops_enabled ? {
    gha-plan = {
      principal_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.gha_plan_role_name}"
      policy_associations = {
        view = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminViewPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
  } : {}
}