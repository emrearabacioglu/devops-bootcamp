# DevOps Bootcamp – Demo Projects and Study Notes

This repo has my work from the TechWorld with Nana DevOps Bootcamp. For every demo project in the bootcamp, there is a folder with the files I wrote while following the demos, and my notes with the commands and terminal output from when I ran them.

**Tools covered:** Linux, Git, DigitalOcean, Nexus, Docker, Docker Compose, Jenkins, AWS (EC2, ECR, IAM, EKS, S3), Kubernetes, Helm, Helmfile, Terraform, Python (Boto3), Ansible, Prometheus, Alertmanager, Grafana.

## Repo structure

```
NN-<module>/
├── 01-demos/
│   ├── README.md            study notes for the whole module
│   ├── 00-basics/           small files from the intro lectures (some modules)
│   └── NN-<demo-project>/   one folder per demo project
│       ├── README.md        short summary: what I built, which file does what, the result
│       ├── NOTES.md         step-by-step notes for this project with terminal output
│       └── ...              project files (Jenkinsfile, Terraform, playbooks, manifests, scripts)
└── 02-projects/
    └── README.md            module exercises
```

## How to read it

- **Quick look at a project:** open the project folder. Its `README.md` explains it in a few lines and shows the result.
- **How it was done, step by step:** `NOTES.md` in the same folder. These are my notes from when I did the demo, with the real commands, output and screenshots.
- **Whole module:** `NN-<module>/01-demos/README.md`. It starts with a contents table and a takeaways list (commands, errors I hit and how I fixed them), then has every demo and the basics lectures in order.

## Modules and demo projects

### [Module 5 – Cloud & Infrastructure as a Service Basics](./05-cloud-basic/01-demos/README.md)

- [Create server and deploy application on DigitalOcean](./05-cloud-basic/01-demos/01-deploy-app-on-digitalocean)

### [Module 6 – Artifact Repository Manager with Nexus](./06-nexus/01-demos/README.md)

- [Run Nexus on Droplet and Publish Artifact to Nexus](./06-nexus/01-demos/01-run-nexus-and-publish-artifacts)

### [Module 7 – Containers with Docker](./07-docker/01-demos/README.md)

- [Use Docker for local development](./07-docker/01-demos/01-docker-for-local-development)
- [Docker Compose - Run multiple Docker containers](./07-docker/01-demos/02-docker-compose)
- [Dockerize Nodejs application](./07-docker/01-demos/03-dockerize-nodejs-app)
- [Create Docker repository on Nexus and push to it](./07-docker/01-demos/04-docker-repo-on-nexus)
- [Deploy Docker application on a server with Docker Compose](./07-docker/01-demos/05-deploy-app-with-docker-compose)
- [Persist data with Docker Volumes](./07-docker/01-demos/06-persist-data-with-volumes)
- [Deploy Nexus as Docker container](./07-docker/01-demos/07-nexus-as-docker-container)

### [Module 8 – Build Automation & CI/CD with Jenkins](./08-jenkins/01-demos/README.md)

- [Install Jenkins on DigitalOcean](./08-jenkins/01-demos/01-install-jenkins-on-digitalocean)
- [Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline)](./08-jenkins/01-demos/02-ci-pipeline-freestyle-pipeline-multibranch)
- [Create a Jenkins Shared Library](./08-jenkins/01-demos/03-jenkins-shared-library)
- [Configure Webhook to trigger CI Pipeline automatically on every change](./08-jenkins/01-demos/04-webhook-trigger-pipeline)
- [Dynamically Increment Application version in Jenkins Pipeline](./08-jenkins/01-demos/05-dynamic-versioning)

### [Module 9 – AWS Services](./09-aws/01-demos/README.md)

- [Deploy Web Application on EC2 Instance (manually)](./09-aws/01-demos/01-deploy-web-app-on-ec2-manually)
- [CD - Deploy Application from Jenkins Pipeline to EC2 Instance (automatically with docker)](./09-aws/01-demos/02-cd-deploy-to-ec2-with-docker)
- [CD - Deploy Application from Jenkins Pipeline on EC2 Instance (automatically with docker-compose)](./09-aws/01-demos/03-cd-deploy-to-ec2-with-docker-compose)
- [Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning)](./09-aws/01-demos/04-complete-cicd-docker-compose-versioning)
- [Create repository on AWS and push to private Docker registry](./09-aws/01-demos/05-push-to-ecr)
- [Interacting with AWS CLI](./09-aws/01-demos/06-aws-cli)

### [Module 10 – Container Orchestration with Kubernetes](./10-kubernetes/01-demos/README.md)

- [Deploy MongoDB and Mongo Express into local K8s cluster](./10-kubernetes/01-demos/01-mongodb-and-mongo-express)
- [Deploy Mosquitto message broker with ConfigMap and Secret Volume Types](./10-kubernetes/01-demos/02-mosquitto-configmap-secret-volumes)
- [Install a stateful service (MongoDB) on Kubernetes using Helm](./10-kubernetes/01-demos/03-helm-mongodb-on-lke)
- [Deploy our web application in K8s cluster from private Docker registry](./10-kubernetes/01-demos/04-deploy-app-from-private-registry)
- [Deploy Microservices application in Kubernetes with Production & Security Best Practices](./10-kubernetes/01-demos/05-microservices-best-practices)
- [Create Helm Chart for Microservices](./10-kubernetes/01-demos/06-helm-chart-and-helmfile)
- [Deploy Microservices with Helmfile](./10-kubernetes/01-demos/06-helm-chart-and-helmfile)

### [Module 11 – Kubernetes on AWS (EKS)](./11-eks/01-demos/README.md)

- [Create AWS EKS cluster with a Node Group](./11-eks/01-demos/01-eks-cluster-with-node-group)
- [Create EKS cluster with Fargate profile](./11-eks/01-demos/02-eks-cluster-with-fargate)
- [Create EKS cluster with eksctl](./11-eks/01-demos/03-eks-cluster-with-eksctl)
- [CD - Deploy to EKS cluster from Jenkins Pipeline](./11-eks/01-demos/04-cd-deploy-to-eks-from-jenkins)
- [Complete CI/CD Pipeline with EKS and private DockerHub registry](./11-eks/01-demos/05-complete-cicd-eks-dockerhub)
- [Complete CI/CD Pipeline with EKS and AWS ECR](./11-eks/01-demos/06-complete-cicd-eks-ecr)

### [Module 12 – Infrastructure as Code with Terraform](./12-terraform/01-demos/README.md)

- [Automate AWS Infrastructure](./12-terraform/01-demos/01-automate-aws-infrastructure)
- [Modularize Project](./12-terraform/01-demos/02-modularize-project)
- [Terraform & AWS EKS](./12-terraform/01-demos/03-terraform-and-eks)
- [Complete CI/CD with Terraform](./12-terraform/01-demos/04-complete-cicd-with-terraform)
- [Configure a Shared Remote State](./12-terraform/01-demos/04-complete-cicd-with-terraform)

### [Module 13 – Programming with Python](./13-python-basic/01-demos/README.md)

- [Write Countdown Application](./13-python-basic/01-demos/01-countdown-app)
- [Automation with Python (Working with Spreadsheets)](./13-python-basic/01-demos/02-spreadsheet-automation)
- [API Request to GitLab (implemented with the GitHub API)](./13-python-basic/01-demos/03-api-request)

### [Module 14 – Automation with Python](./14-python-automation/01-demos/README.md)

- [Health Check: EC2 Status Checks](./14-python-automation/01-demos/01-ec2-status-checks)
- [Automate configuring EC2 Server Instances](./14-python-automation/01-demos/02-configure-ec2-instances)
- [Automate displaying EKS cluster information](./14-python-automation/01-demos/03-eks-cluster-info)
- [Data Backup & Restore](./14-python-automation/01-demos/04-data-backup-restore)
- [Website Monitoring and Recovery](./14-python-automation/01-demos/05-website-monitoring-recovery)

### [Module 15 – Configuration Management with Ansible](./15-ansible/01-demos/README.md)

- [Automate Node.js application Deployment](./15-ansible/01-demos/01-automate-nodejs-deployment)
- [Automate Nexus Deployment](./15-ansible/01-demos/02-automate-nexus-deployment)
- [Ansible & Docker](./15-ansible/01-demos/03-ansible-and-docker)
- [Ansible Integration in Terraform](./15-ansible/01-demos/04-ansible-integration-in-terraform)
- [Configure Dynamic Inventory](./15-ansible/01-demos/05-configure-dynamic-inventory)
- [Automate Kubernetes Deployment](./15-ansible/01-demos/06-automate-kubernetes-deployment)
- [Ansible Integration in Jenkins](./15-ansible/01-demos/07-ansible-integration-in-jenkins)
- [Structure Playbooks with Ansible Roles](./15-ansible/01-demos/08-ansible-roles)

### [Module 16 – Monitoring with Prometheus](./16-prometheus/01-demos/README.md)

- [Install Prometheus Stack in Kubernetes](./16-prometheus/01-demos/01-install-prometheus-stack)
- [Configure Alerting for our Application](./16-prometheus/01-demos/02-configure-alerting)
- [Configure Monitoring for a Third-Party Application](./16-prometheus/01-demos/03-monitoring-third-party-app)
- [Configure Monitoring for Own Application](./16-prometheus/01-demos/04-monitoring-own-app)

## Notes

- The code is kept as I wrote it in the demos. It follows the course projects and isn't refactored afterwards.
- Passwords, tokens and keys are replaced with `***`. Files with real values (`terraform.tfvars`, `project-vars`, kubeconfigs) are not committed; `terraform.tfvars.example` files show which variables are needed.
- The servers and clusters in the notes were deleted after each demo, so the IPs and endpoints in the logs are no longer in use.
