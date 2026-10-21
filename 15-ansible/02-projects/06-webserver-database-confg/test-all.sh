#!/usr/bin/env bash
# End-to-end test for exercise 6: control node -> web + db -> app check -> destroy
set -euo pipefail
step() { echo; echo "===== $1 ====="; }
on_control() {   # run a command on the Ansible server and show its output
  ansible tag_Role_ansible_server -m ansible.builtin.shell \
    -a "cd ~/control-node && ~/.local/bin/$1"
}
trap 'echo; echo "!!! FAILED. Resources may still exist. Clean up with:";
      echo "  ansible tag_Role_ansible_server -m shell -a \"cd ~/control-node && ~/.local/bin/ansible-playbook destroy-resources.yaml\"";
      echo "  ansible-playbook terminate-control-node.yaml"' ERR

step "Provision Ansible server"
ansible-playbook provision-ansible-server.yaml || {
  echo "retrying once (IAM instance profile can take a few seconds to appear)"
  sleep 15; ansible-playbook provision-ansible-server.yaml; }

step "Wait for SSH (max 3 min)"
for i in $(seq 1 18); do
  ansible tag_Role_ansible_server -m ping -o && break
  echo "not ready yet ($i/18)"; sleep 10
done
ansible tag_Role_ansible_server -m ping -o

step "Configure Ansible server"
ansible-playbook configure-ansible-server.yaml

step "On control node: inventory before provisioning"
on_control "ansible-inventory --graph"

step "On control node: provision web + db (NAT takes a few minutes)"
on_control "ansible-playbook provision-webserver-db.yaml"

step "On control node: inventory after provisioning"
on_control "ansible-inventory --graph"

step "On control node: configure MySQL + deploy Java app"
on_control "ansible-playbook configure-webserver-db.yaml"

step "App reachable from the internet on 8080 (max 2 min)"
WEB_IP=$(aws ec2 describe-instances \
  --filters Name=tag:Role,Values=web-server Name=instance-state-name,Values=running \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "web server: http://$WEB_IP:8080"
for i in $(seq 1 12); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://$WEB_IP:8080" || true)
  echo "HTTP $code"; [ "$code" = "200" ] && break; sleep 10
done
[ "$code" = "200" ]

echo; echo "===== APP IS UP: http://$WEB_IP:8080 ====="
read -r -t 600 -p "Press Enter to destroy now (auto-destroy in 10 min)... " || true

step "On control node: destroy web + db + network"
on_control "ansible-playbook destroy-resources.yaml"

step "Destroy Ansible server, its SG, IAM role, key pair"
ansible-playbook terminate-control-node.yaml

echo; echo "===== ALL DONE ====="