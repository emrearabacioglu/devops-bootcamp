# Copy these into the GitHub repository variables
# AWS_PLAN_ROLE_ARN, AWS_APPLY_ROLE_ARN and AWS_ECR_PUSH_ROLE_ARN.
output "plan_role_arn" {
  value = aws_iam_role.plan.arn
}

output "apply_role_arn" {
  value = aws_iam_role.apply.arn
}

output "ecr_push_role_arn" {
  value = aws_iam_role.ecr_push.arn
}
