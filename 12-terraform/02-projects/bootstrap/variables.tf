variable "github_repository" {
  description = "GitHub repository (owner/name) whose workflows may assume the roles."
  type        = string
  default     = "emrearabacioglu/devops-bootcamp"
}

variable "environments" {
  description = "GitHub Environments that may assume the apply role. Each one has required reviewers."
  type        = list(string)
  default     = ["dev", "test", "staging"]
}

variable "state_bucket" {
  description = "S3 bucket with the Terraform state of the environments."
  type        = string
  default     = "emre-myapp-tfstate-10"
}

variable "ecr_repository" {
  description = "ECR repository the app workflow pushes to. Created once, outside Terraform."
  type        = string
  default     = "java-app"
}
