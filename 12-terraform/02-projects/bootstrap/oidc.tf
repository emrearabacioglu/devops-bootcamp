data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  oidc_host  = "token.actions.githubusercontent.com"
  repo       = var.github_repository
}

# GitHub's OIDC issuer. Workflows exchange a short-lived GitHub token for
# temporary AWS credentials, so no access keys are stored in GitHub.
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://${local.oidc_host}"
  client_id_list = ["sts.amazonaws.com"]
}

# Builds a trust policy that only accepts tokens from this repository
# with one of the given `sub` claims.
data "aws_iam_policy_document" "trust" {
  for_each = {
    plan     = ["repo:${local.repo}:pull_request", "repo:${local.repo}:ref:refs/heads/main"]
    apply    = [for env in var.environments : "repo:${local.repo}:environment:${env}"]
    ecr_push = ["repo:${local.repo}:ref:refs/heads/main"]
  }

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:sub"
      values   = each.value
    }
  }
}

# --- plan: read-only, used by PRs and by the plan job before approval ---

resource "aws_iam_role" "plan" {
  name                 = "gha-terraform-plan"
  assume_role_policy   = data.aws_iam_policy_document.trust["plan"].json
  max_session_duration = 3600
}

resource "aws_iam_role_policy_attachment" "plan_readonly" {
  role       = aws_iam_role.plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

data "aws_iam_policy_document" "plan_extra" {
  # Read and lock the state, create the workspace on the first plan.
  statement {
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.state_bucket}"]
  }
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["arn:aws:s3:::${var.state_bucket}/*"]
  }
  # ReadOnlyAccess doesn't include secret values, but refreshing
  # aws_secretsmanager_secret_version needs them.
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = ["arn:aws:secretsmanager:*:${local.account_id}:secret:*/myapp/db-*"]
  }
}

resource "aws_iam_role_policy" "plan_extra" {
  name   = "state-and-db-secret"
  role   = aws_iam_role.plan.id
  policy = data.aws_iam_policy_document.plan_extra.json
}

# --- apply: only reachable from a job that runs in an approved GitHub Environment ---

resource "aws_iam_role" "apply" {
  name                 = "gha-terraform-apply"
  assume_role_policy   = data.aws_iam_policy_document.trust["apply"].json
  max_session_duration = 7200 # creating or destroying an EKS environment takes ~20 minutes
}

# The environment project creates IAM roles, a VPC, EKS and more, so the
# role needs broad rights. What protects it is the trust policy above.
resource "aws_iam_role_policy_attachment" "apply_admin" {
  role       = aws_iam_role.apply.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# --- ecr_push: the app workflow, push to one repository only ---

resource "aws_iam_role" "ecr_push" {
  name                 = "gha-ecr-push"
  assume_role_policy   = data.aws_iam_policy_document.trust["ecr_push"].json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "ecr_push" {
  statement {
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = ["arn:aws:ecr:eu-central-1:${local.account_id}:repository/${var.ecr_repository}"]
  }
}

resource "aws_iam_role_policy" "ecr_push" {
  name   = "push-${var.ecr_repository}"
  role   = aws_iam_role.ecr_push.id
  policy = data.aws_iam_policy_document.ecr_push.json
}
