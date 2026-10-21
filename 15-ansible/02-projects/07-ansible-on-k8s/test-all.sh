#!/usr/bin/env bash
# End-to-end test: EKS -> image -> single MySQL -> migrate to MySQL chart -> destroy
set -euo pipefail
step() { echo; echo "===== $1 ====="; }
app_url() { echo "http://$(kubectl get ingress java-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"; }
check_app() {   # wait until the app answers 200 through the load balancer (max 5 min, DNS can be slow)
  local url; url=$(app_url); echo "app: $url"
  for i in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)
    echo "HTTP $code"; [ "$code" = "200" ] && return 0; sleep 10
  done
  return 1
}
trap 'echo; echo "!!! FAILED. Resources may still exist. Clean up with: ansible-playbook destroy.yaml"' ERR

step "Syntax check"
ansible-playbook build-image-push-to-ecr.yaml deploy-to-cluster.yaml migrate-mysql-to-helm.yaml destroy.yaml --syntax-check

step "Terraform: VPC + EKS (about 15 min)"
terraform -chdir=terraform init -input=false
terraform -chdir=terraform apply -auto-approve -var-file=environments/dev.tfvars

step "Build and push image to ECR"
ansible-playbook build-image-push-to-ecr.yaml

step "Deploy: ingress-nginx, single MySQL, Java app"
ansible-playbook deploy-to-cluster.yaml
kubectl get pods -o wide
check_app

step "Migrate: MySQL chart (1 primary + 2 secondaries)"
ansible-playbook migrate-mysql-to-helm.yaml
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql --timeout=300s
kubectl get pods,pvc -o wide
echo "MySQL pods: $(kubectl get pods -l app.kubernetes.io/instance=mysql --no-headers | wc -l) (expected 3)"
echo "Java app DB_SERVER: $(kubectl exec deploy/java-app-deployment -- printenv DB_SERVER) (expected mysql-primary)"
! kubectl get deployment mysql-deployment 2>/dev/null && echo "old mysql-deployment is gone"
check_app

echo; echo "===== APP IS UP: $(app_url) ====="
read -r -t 600 -p "Press Enter to destroy now (auto-destroy in 10 min)... " || true

step "Destroy"
ansible-playbook destroy.yaml

step "Leftover check (should all be 0)"
echo "EBS volumes from the cluster: $(aws ec2 describe-volumes --filters Name=tag-key,Values=ebs.csi.aws.com/cluster --query 'length(Volumes)' --output text)"
echo "Classic load balancers:       $(aws elb describe-load-balancers --query 'length(LoadBalancerDescriptions)' --output text)"
echo "ALB/NLB load balancers:       $(aws elbv2 describe-load-balancers --query 'length(LoadBalancers)' --output text)"

echo; echo "===== ALL DONE ====="