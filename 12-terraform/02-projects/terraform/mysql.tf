resource "helm_release" "mysql" {
  name       = "mysql"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "mysql"
  version    = "14.0.3"
  namespace  = "default"

  values = [file("${path.module}/values/mysql-values.yaml")]

  set_sensitive = [{
    name  = "auth.rootPassword"
    value = var.mysql_root_password
  }]

  depends_on = [module.eks]
}