# DevOps Bootcamp – Projects, Demos and Study Notes

This repo has my work from the TechWorld with Nana DevOps Bootcamp. Every module has two parts: the demo projects I built while following the lectures, with my notes and the terminal output from when I ran them, and the projects I built on my own at the end of the module.

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
    ├── README.md            the module's projects: what I built, how it works, the result
    └── ...                  project files, or one folder per project when the module has several
```

## How to read it

- **Projects:** start with the [table below](#projects). Each project's `README.md` explains what it does, how it works, the decisions behind it and the result.
- **Quick look at a demo:** open the demo folder. Its `README.md` explains it in a few lines and shows the result.
- **How a demo was done, step by step:** `NOTES.md` in the same folder. These are my notes from when I did the demo, with the real commands, output and screenshots.
- **Whole module:** `NN-<module>/01-demos/README.md`. It starts with a contents table and a takeaways list (commands, errors I hit and how I fixed them), then has every demo and the basics lectures in order.

## Projects

The larger projects, check README:

| Project | What it does | Main tools |
|---|---|---|
| [Java app with MySQL on EKS, deployed by a Jenkins pipeline](./11-eks/02-projects) | EKS cluster with an EC2 node group for MySQL and Fargate for the app. A Jenkins pipeline bumps the version, pushes the image to ECR and deploys everything with Helmfile. | EKS, Fargate, eksctl, Jenkins, Helmfile, ECR |
| [EKS environments with Terraform and two Jenkins pipelines](./12-terraform/02-projects) | One Terraform project creates `dev`, `test` and `staging` EKS environments with their own S3 state, Cluster Autoscaler and MySQL. One pipeline manages the infrastructure, another deploys the app. | Terraform, EKS, S3, Cluster Autoscaler, Jenkins, Helmfile |
| [Run and monitor nginx on EC2 with Python](./14-python-automation/02-projects/01-run-and-monitor-nginx-on-ec2) | One script creates an EC2 instance, installs Docker over SSH, starts nginx and restarts it when it stops answering. | Python, boto3, paramiko, EC2, Docker |
| [Deploy an ECR image to EC2 from a Jenkins pipeline with Python](./14-python-automation/02-projects/02-deploy-ecr-image-from-jenkins) | Jenkins lists the image tags in ECR, the user picks one, Python scripts deploy it to EC2 and check that the selected version is running. | Python, boto3, Jenkins, ECR, EC2 |
| [Jenkins server on EC2 (Amazon Linux or Ubuntu)](./15-ansible/02-projects/04-setup-with-distro-input) | Ansible creates an EC2 server with the chosen distro and installs Jenkins, Docker and Node.js on it. | Ansible roles, dynamic inventory, EC2 |
| [Jenkins as a Docker container on EC2](./15-ansible/02-projects/05-setup-jenkins-container) | The same server with Jenkins in a custom container that builds with the host's Docker. | Ansible, Docker, Jenkins, EC2 |
| [Java web app and MySQL on AWS, managed from a dedicated Ansible control node](./15-ansible/02-projects/06-webserver-database-confg) | A VPC with public and private subnets, a web server and a database server, all configured from an Ansible control node inside AWS. | Ansible, VPC, EC2, IAM, MySQL |
| [Java app with MySQL on EKS, deployed and migrated with Ansible](./15-ansible/02-projects/07-ansible-on-k8s) | Ansible builds the app image, deploys it to EKS with an ingress, then replaces the single MySQL with a replicated Helm chart while the app keeps running. | Ansible, Terraform, EKS, Helm, ingress-nginx |
| [Monitoring and alerting for a Java app with MySQL on EKS](./16-prometheus/02-projects) | Prometheus scrapes the ingress, MySQL and the app, five alert rules watch them, and Alertmanager routes the alerts to Slack or email. | Prometheus, Alertmanager, Ansible, EKS |

## Modules

### [Module 5 – Cloud & Infrastructure as a Service Basics](./05-cloud-basic/01-demos/README.md)

**Demos**

- [Create server and deploy application on DigitalOcean](./05-cloud-basic/01-demos/01-deploy-app-on-digitalocean)

**Projects**

- [Package a Node.js app and run it on a DigitalOcean droplet](./05-cloud-basic/02-projects)

### [Module 6 – Artifact Repository Manager with Nexus](./06-nexus/01-demos/README.md)

**Demos**

- [Run Nexus on Droplet and Publish Artifact to Nexus](./06-nexus/01-demos/01-run-nexus-and-publish-artifacts)

**Projects**

- [Publish npm and Maven artifacts to Nexus and run the app from Nexus](./06-nexus/02-projects)

### [Module 7 – Containers with Docker](./07-docker/01-demos/README.md)

**Demos**

- [Use Docker for local development](./07-docker/01-demos/01-docker-for-local-development)
- [Docker Compose - Run multiple Docker containers](./07-docker/01-demos/02-docker-compose)
- [Dockerize Nodejs application](./07-docker/01-demos/03-dockerize-nodejs-app)
- [Create Docker repository on Nexus and push to it](./07-docker/01-demos/04-docker-repo-on-nexus)
- [Deploy Docker application on a server with Docker Compose](./07-docker/01-demos/05-deploy-app-with-docker-compose)
- [Persist data with Docker Volumes](./07-docker/01-demos/06-persist-data-with-volumes)
- [Deploy Nexus as Docker container](./07-docker/01-demos/07-nexus-as-docker-container)

**Projects**

- [Java app with MySQL and phpMyAdmin in Docker Compose, pushed to Nexus and deployed to a server](./07-docker/02-projects)

### [Module 8 – Build Automation & CI/CD with Jenkins](./08-jenkins/01-demos/README.md)

**Demos**

- [Install Jenkins on DigitalOcean](./08-jenkins/01-demos/01-install-jenkins-on-digitalocean)
- [Create a CI Pipeline with Jenkinsfile (Freestyle, Pipeline, Multibranch Pipeline)](./08-jenkins/01-demos/02-ci-pipeline-freestyle-pipeline-multibranch)
- [Create a Jenkins Shared Library](./08-jenkins/01-demos/03-jenkins-shared-library)
- [Configure Webhook to trigger CI Pipeline automatically on every change](./08-jenkins/01-demos/04-webhook-trigger-pipeline)
- [Dynamically Increment Application version in Jenkins Pipeline](./08-jenkins/01-demos/05-dynamic-versioning)

### [Module 9 – AWS Services](./09-aws/01-demos/README.md)

**Demos**

- [Deploy Web Application on EC2 Instance (manually)](./09-aws/01-demos/01-deploy-web-app-on-ec2-manually)
- [CD - Deploy Application from Jenkins Pipeline to EC2 Instance (automatically with docker)](./09-aws/01-demos/02-cd-deploy-to-ec2-with-docker)
- [CD - Deploy Application from Jenkins Pipeline on EC2 Instance (automatically with docker-compose)](./09-aws/01-demos/03-cd-deploy-to-ec2-with-docker-compose)
- [Complete the CI/CD Pipeline (Docker-Compose, Dynamic versioning)](./09-aws/01-demos/04-complete-cicd-docker-compose-versioning)
- [Create repository on AWS and push to private Docker registry](./09-aws/01-demos/05-push-to-ecr)
- [Interacting with AWS CLI](./09-aws/01-demos/06-aws-cli)

**Projects**

- [Node.js app on EC2, deployed by a Jenkins pipeline with Docker Compose](./09-aws/02-projects)

### [Module 10 – Container Orchestration with Kubernetes](./10-kubernetes/01-demos/README.md)

**Demos**

- [Deploy MongoDB and Mongo Express into local K8s cluster](./10-kubernetes/01-demos/01-mongodb-and-mongo-express)
- [Deploy Mosquitto message broker with ConfigMap and Secret Volume Types](./10-kubernetes/01-demos/02-mosquitto-configmap-secret-volumes)
- [Install a stateful service (MongoDB) on Kubernetes using Helm](./10-kubernetes/01-demos/03-helm-mongodb-on-lke)
- [Deploy our web application in K8s cluster from private Docker registry](./10-kubernetes/01-demos/04-deploy-app-from-private-registry)
- [Deploy Microservices application in Kubernetes with Production & Security Best Practices](./10-kubernetes/01-demos/05-microservices-best-practices)
- [Create Helm Chart for Microservices](./10-kubernetes/01-demos/06-helm-chart-and-helmfile)
- [Deploy Microservices with Helmfile](./10-kubernetes/01-demos/06-helm-chart-and-helmfile)

**Projects**

- [Java app with replicated MySQL, phpMyAdmin and Ingress on Kubernetes, packaged as a Helm chart](./10-kubernetes/02-projects)

### [Module 11 – Kubernetes on AWS (EKS)](./11-eks/01-demos/README.md)

**Demos**

- [Create AWS EKS cluster with a Node Group](./11-eks/01-demos/01-eks-cluster-with-node-group)
- [Create EKS cluster with Fargate profile](./11-eks/01-demos/02-eks-cluster-with-fargate)
- [Create EKS cluster with eksctl](./11-eks/01-demos/03-eks-cluster-with-eksctl)
- [CD - Deploy to EKS cluster from Jenkins Pipeline](./11-eks/01-demos/04-cd-deploy-to-eks-from-jenkins)
- [Complete CI/CD Pipeline with EKS and private DockerHub registry](./11-eks/01-demos/05-complete-cicd-eks-dockerhub)
- [Complete CI/CD Pipeline with EKS and AWS ECR](./11-eks/01-demos/06-complete-cicd-eks-ecr)

**Projects**

- [Java app with MySQL on EKS, deployed by a Jenkins pipeline](./11-eks/02-projects)

### [Module 12 – Infrastructure as Code with Terraform](./12-terraform/01-demos/README.md)

**Demos**

- [Automate AWS Infrastructure](./12-terraform/01-demos/01-automate-aws-infrastructure)
- [Modularize Project](./12-terraform/01-demos/02-modularize-project)
- [Terraform & AWS EKS](./12-terraform/01-demos/03-terraform-and-eks)
- [Complete CI/CD with Terraform](./12-terraform/01-demos/04-complete-cicd-with-terraform)
- [Configure a Shared Remote State](./12-terraform/01-demos/04-complete-cicd-with-terraform)

**Projects**

- [EKS environments with Terraform and two Jenkins pipelines](./12-terraform/02-projects)

### [Module 13 – Programming with Python](./13-python-basic/01-demos/README.md)

**Demos**

- [Write Countdown Application](./13-python-basic/01-demos/01-countdown-app)
- [Automation with Python (Working with Spreadsheets)](./13-python-basic/01-demos/02-spreadsheet-automation)
- [API Request to GitLab (implemented with the GitHub API)](./13-python-basic/01-demos/03-api-request)

**Projects**

- [Python basics: data structures, functions, classes, spreadsheets and the GitHub API](./13-python-basic/02-projects)

### [Module 14 – Automation with Python](./14-python-automation/01-demos/README.md)

**Demos**

- [Health Check: EC2 Status Checks](./14-python-automation/01-demos/01-ec2-status-checks)
- [Automate configuring EC2 Server Instances](./14-python-automation/01-demos/02-configure-ec2-instances)
- [Automate displaying EKS cluster information](./14-python-automation/01-demos/03-eks-cluster-info)
- [Data Backup & Restore](./14-python-automation/01-demos/04-data-backup-restore)
- [Website Monitoring and Recovery](./14-python-automation/01-demos/05-website-monitoring-recovery)

**Projects**

- [Run and monitor nginx on EC2 with Python](./14-python-automation/02-projects/01-run-and-monitor-nginx-on-ec2)
- [Deploy an ECR image to EC2 from a Jenkins pipeline with Python](./14-python-automation/02-projects/02-deploy-ecr-image-from-jenkins)
- [Smaller boto3 scripts: subnets, IAM users, ECR images](./14-python-automation/02-projects/scripts)

### [Module 15 – Configuration Management with Ansible](./15-ansible/01-demos/README.md)

**Demos**

- [Automate Node.js application Deployment](./15-ansible/01-demos/01-automate-nodejs-deployment)
- [Automate Nexus Deployment](./15-ansible/01-demos/02-automate-nexus-deployment)
- [Ansible & Docker](./15-ansible/01-demos/03-ansible-and-docker)
- [Ansible Integration in Terraform](./15-ansible/01-demos/04-ansible-integration-in-terraform)
- [Configure Dynamic Inventory](./15-ansible/01-demos/05-configure-dynamic-inventory)
- [Automate Kubernetes Deployment](./15-ansible/01-demos/06-automate-kubernetes-deployment)
- [Ansible Integration in Jenkins](./15-ansible/01-demos/07-ansible-integration-in-jenkins)
- [Structure Playbooks with Ansible Roles](./15-ansible/01-demos/08-ansible-roles)

**Projects**

- [Build and deploy a Java app to an Ubuntu server with Ansible](./15-ansible/02-projects/01-deploy-java-app)
- [Jenkins server on Amazon Linux EC2 with Ansible](./15-ansible/02-projects/02-setup-jenkins-server-ec2)
- [Jenkins server on Ubuntu EC2 with Ansible](./15-ansible/02-projects/03-setup-jenkins-server-ubuntu)
- [Jenkins server on EC2 (Amazon Linux or Ubuntu)](./15-ansible/02-projects/04-setup-with-distro-input)
- [Jenkins as a Docker container on EC2](./15-ansible/02-projects/05-setup-jenkins-container)
- [Java web app and MySQL on AWS, managed from a dedicated Ansible control node](./15-ansible/02-projects/06-webserver-database-confg)
- [Java app with MySQL on EKS, deployed and migrated with Ansible](./15-ansible/02-projects/07-ansible-on-k8s)

### [Module 16 – Monitoring with Prometheus](./16-prometheus/01-demos/README.md)

**Demos**

- [Install Prometheus Stack in Kubernetes](./16-prometheus/01-demos/01-install-prometheus-stack)
- [Configure Alerting for our Application](./16-prometheus/01-demos/02-configure-alerting)
- [Configure Monitoring for a Third-Party Application](./16-prometheus/01-demos/03-monitoring-third-party-app)
- [Configure Monitoring for Own Application](./16-prometheus/01-demos/04-monitoring-own-app)

**Projects**

- [Monitoring and alerting for a Java app with MySQL on EKS](./16-prometheus/02-projects)

## Notes

- The code is kept as I wrote it in the demos. It follows the course projects and isn't refactored afterwards.
- Passwords, tokens and keys are replaced with `***`. Files with real values (`terraform.tfvars`, `project-vars`, kubeconfigs) are not committed; `terraform.tfvars.example` files show which variables are needed.
- The servers and clusters in the notes were deleted after each demo, so the IPs and endpoints in the logs are no longer in use.
