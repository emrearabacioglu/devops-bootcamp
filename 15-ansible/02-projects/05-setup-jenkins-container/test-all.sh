#!/usr/bin/env bash
# Full test run: provision both distros, install Jenkins, verify
set -euo pipefail
step() { echo; echo "===== $1 ====="; }

step "Syntax check"
ansible-playbook provision.yaml setup-jenkins.yaml destroy-instance.yaml --syntax-check

step "Provision ubuntu + amazon"
ansible-playbook provision.yaml -e os=ubuntu
ansible-playbook provision.yaml -e os=amazon

step "Wait for SSH (max 3 min)"
for i in $(seq 1 18); do
  ansible all -m ping -o && break
  echo "not ready yet ($i/18)"; sleep 10
done
ansible all -m ping -o

step "Inventory"
ansible-inventory --graph

step "Setup Jenkins on both"
ansible-playbook setup-jenkins.yaml

step "Second run (should be mostly ok, not changed)"
ansible-playbook setup-jenkins.yaml

step "Jenkins responds on 8080 (max 2 min)"
for i in $(seq 1 12); do
  ansible all -m uri -a "url=http://localhost:8080/login" -o && break
  echo "Jenkins starting ($i/12)"; sleep 10
done
ansible all -m uri -a "url=http://localhost:8080/login" -o

step "Tools inside the container (as jenkins user)"
ansible all -b -m command -a "docker exec jenkins id"
ansible all -b -m command -a "docker exec jenkins docker ps"
ansible all -b -m command -a "docker exec jenkins node -v"
ansible all -b -m command -a "docker exec jenkins npm -v"

echo; echo "===== ALL TESTS PASSED ====="