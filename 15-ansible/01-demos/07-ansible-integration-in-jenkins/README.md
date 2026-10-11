# Ansible Integration in Jenkins

**Technologies:** Ansible, Jenkins, DigitalOcean, AWS, Boto3, Docker, Java, Maven, Linux, Git

I set up a Jenkins pipeline that copies the Ansible files and the EC2 SSH key to a separate Ansible control node and runs the playbook there. The playbook installs Docker and Docker Compose on 2 EC2 instances.

## Summary
1. Servers:
   - Jenkins runs in a Docker container on a DigitalOcean droplet.
   - The Ansible control node is a second droplet (Ubuntu) with AWS credentials configured, so the `aws_ec2` inventory plugin can query EC2.
   - The 2 managed nodes are EC2 instances (Amazon Linux 2023) created with `terraform/` in the default VPC. They use a dedicated key pair `ansible-jenkins`, and the security group allows SSH from my IP and from the control node. `terraform/terraform.tfvars.example` shows the variables, with `my_ip` masked.
2. The `Jenkinsfile` and the `ansible/` folder are inside `java-maven-app/`. `ansible/` has:
   - `ansible.cfg`: dynamic inventory, `remote_user = ec2-user` and the key `~/ssh-key.pem` that Jenkins copies to the control node.
   - `inventory_aws_ec2.yaml`: the `aws_ec2` plugin config.
   - `jenkins-playbook.yaml`: installs Docker and Docker Compose on all EC2 instances.
3. Stage "Copy files to ansible-server": with `sshagent` it copies `ansible/*` to the control node with `scp`, then copies the EC2 private key from the `ec2-server-key` credential to `/root/ssh-key.pem`.
4. Stage "Configure EC2 instances with ansible": with SSH Pipeline Steps, `sshScript` runs `java-maven-app/prepare-ansible-server.sh` on the control node (installs Ansible and `python3-boto3` with apt), then `sshCommand` runs `ansible-playbook jenkins-playbook.yaml` there. The control node IP is set once as `ANSIBLE_SERVER`.
5. The paths in the `Jenkinsfile` start with `07-jenkins-integration/java-maven-app/`, the folder name in the repo the job ran from. The other files in `java-maven-app/` (`pom.xml`, `src/`, `script.groovy`) are from the bootcamp's Java Maven app; this pipeline doesn't use them.

## Jenkins setup
- Plugins: SSH Agent and SSH Pipeline Steps.
- Credentials (SSH Username with private key): `ansible-server-key` (user `root` + key for the control node) and `ec2-server-key` (user `ec2-user` + private key of the `ansible-jenkins` key pair).
- Pipeline job: "Pipeline script from SCM", Script Path `07-jenkins-integration/java-maven-app/Jenkinsfile`.

## Result
Console output of the pipeline: the control node is prepared, the playbook configures both EC2 instances and the build ends with `SUCCESS`:
```
[Pipeline] sshScript
Executing script on ansible-server[164.92.224.167]: /var/jenkins_home/workspace/ansible-pipeline/07-jenkins-integration/java-maven-app/prepare-ansible-server.sh
...
ansible is already the newest version (9.2.0+dfsg-0ubuntu5).
...
python3-boto3 is already the newest version (1.34.46+dfsg-1ubuntu1).
[Pipeline] sshCommand
Executing command on ansible-server[164.92.224.167]: ansible-playbook jenkins-playbook.yaml sudo: false
...
PLAY RECAP ****
ec2-18-156-36-106.eu-central-1.compute.amazonaws.com : ok=7    changed=5    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ec2-3-121-232-17.eu-central-1.compute.amazonaws.com : ok=7    changed=5    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

Finished: SUCCESS
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
