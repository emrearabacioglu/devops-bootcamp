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

variable "gha_apply_role_name" {
  description = "IAM role of the apply job (from ../bootstrap). Gets cluster admin when gitops_enabled."
  type        = string
  default     = "gha-terraform-apply"
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

  account_id     = data.aws_caller_identity.current.account_id
  apply_role_arn = "arn:aws:iam::${local.account_id}:role/${var.gha_apply_role_name}"

  # The EKS module finds the "cluster creator" at plan time. In GitHub Actions the
  # plan job (read-only role) and the apply job (apply role) are different identities,
  # so the creator would be the plan role. With gitops_enabled the creator entry is
  # off and the apply role is named explicitly instead.
  apply_access_entry = var.gitops_enabled ? {
    gha-apply = {
      principal_arn = local.apply_role_arn
      policy_associations = {
        admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
  } : {}

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