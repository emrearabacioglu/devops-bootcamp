module "cluster_autoscaler_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.0"
  name    = "${local.cluster_name}-autoscaler"

  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = [module.eks.cluster_name]

  associations = {
    this = {
      cluster_name    = module.eks.cluster_name
      namespace       = "kube-system"
      service_account = "cluster-autoscaler"
    }
  }
}

resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  version    = "9.59.0"
  namespace  = "kube-system"
  set = [
    {
      name  = "autoDiscovery.clusterName"
      value = module.eks.cluster_name
    },
    {
      name  = "awsRegion"
      value = "eu-central-1"
    },
    {
      name  = "rbac.serviceAccount.name"
      value = "cluster-autoscaler"
    }
  ]
  depends_on = [module.eks, module.cluster_autoscaler_pod_identity]
}