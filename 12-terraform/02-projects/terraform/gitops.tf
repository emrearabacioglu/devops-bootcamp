# GitHub Actions + Argo CD version only (var.gitops_enabled).
# Terraform installs the platform: the DB secret in Secrets Manager, External
# Secrets Operator and Argo CD. Argo CD then deploys the app from Git.

locals {
  gitops       = var.gitops_enabled ? 1 : 0
  gitops_path  = "12-terraform/02-projects/app/gitops/envs/${var.env_prefix}"
  db_secret_id = "${var.env_prefix}/myapp/db"
}

# --- DB credentials for the app, read into the cluster by External Secrets ---

resource "aws_secretsmanager_secret" "db" {
  count = local.gitops
  name  = local.db_secret_id

  # Delete at once on destroy, so the environment can be recreated with the same name.
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db" {
  count     = local.gitops
  secret_id = aws_secretsmanager_secret.db[0].id
  secret_string = jsonencode({
    DB_USER = "root"
    DB_PWD  = var.mysql_root_password
    DB_NAME = "my-app-db"
  })
}

# --- External Secrets Operator ---

module "external_secrets_pod_identity" {
  count   = local.gitops
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.0"
  name    = "${local.cluster_name}-external-secrets"

  attach_external_secrets_policy        = true
  external_secrets_secrets_manager_arns = [aws_secretsmanager_secret.db[0].arn]

  associations = {
    this = {
      cluster_name    = module.eks.cluster_name
      namespace       = "external-secrets"
      service_account = "external-secrets"
    }
  }
}

resource "helm_release" "external_secrets" {
  count            = local.gitops
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  version          = "2.15.0"
  namespace        = "external-secrets"
  create_namespace = true

  values = [yamlencode({
    serviceAccount = { name = "external-secrets" }
  })]

  depends_on = [module.eks, module.external_secrets_pod_identity]
}

# --- Argo CD ---

resource "helm_release" "argocd" {
  count            = local.gitops
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "10.18.2"
  namespace        = "argocd"
  create_namespace = true

  # No SSO and no notifications: two pods less on the node group.
  values = [yamlencode({
    dex           = { enabled = false }
    notifications = { enabled = false }
  })]

  depends_on = [module.eks]
}

# App of apps: one root Application per environment that syncs every
# Application manifest in app/gitops/envs/<env>/.
resource "helm_release" "argocd_root_app" {
  count      = local.gitops
  name       = "argocd-root-app"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = "2.0.8"
  namespace  = "argocd"

  values = [yamlencode({
    applications = {
      root = {
        namespace = "argocd"
        project   = "default"
        source = {
          repoURL        = var.gitops_repo_url
          targetRevision = var.gitops_revision
          path           = local.gitops_path
        }
        destination = {
          server    = "https://kubernetes.default.svc"
          namespace = "argocd"
        }
        syncPolicy = {
          automated = { prune = true, selfHeal = true }
        }
      }
    }
  })]

  # The child apps need the ExternalSecret CRDs and the MySQL service.
  depends_on = [helm_release.argocd, helm_release.external_secrets, helm_release.mysql]
}
