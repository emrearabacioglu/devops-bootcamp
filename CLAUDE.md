# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portfolio of study work from the TechWorld with Nana DevOps Bootcamp, modules 05–16 (DigitalOcean, Nexus, Docker, Jenkins, AWS, Kubernetes, EKS, Terraform, Python, Ansible, Prometheus). It is mostly documentation plus the infrastructure and automation files that go with it. There is no build system, linter or test suite at the root. Every project runs against real cloud resources (AWS `eu-central-1` mostly, some DigitalOcean/Linode), so nothing here can be "run" locally without credentials and a live account.

## Layout and doc conventions

```
NN-<module>/
├── 01-demos/
│   ├── README.md            module study notes: Contents table, Takeaways list, then every demo in <details> blocks
│   └── NN-<demo>/
│       ├── README.md        short: Technologies, one-paragraph intro, Summary (numbered), Run, Result, link to NOTES.md
│       ├── NOTES.md         step-by-step notes with the real commands and terminal output
│       └── ...files
└── 02-projects/
    ├── README.md            the module's own projects
    └── ...files (or one folder per project)
```

- Larger project READMEs follow this section order: `**Technologies:**` line, intro, `## How it works` (ASCII flow diagram + a "File | What it does" table), `### Decisions`, `## Requirements`, `## Usage`, `## Testing` (when present), `## Result`.
- Writing style: first person ("I deployed…"), short plain sentences, no marketing language. Terminal output is real, pasted from runs, with prompts like `root@PC:~/modules/<module>/...#`; in module and NOTES files it is indented 4 spaces inside the fenced block. Don't invent output.
- The root `README.md` has a "Projects" table and a per-module list of demos/projects with relative links. When adding, renaming or moving a demo or project, update those links (and the module's `01-demos/README.md` contents table).
- Jenkins jobs reference files by repo path (e.g. Script Path `12-terraform/02-projects/terraform/Jenkinsfile`, `11-eks/02-projects/Jenkinsfile`). Moving folders breaks those jobs, and the READMEs that name the paths must be updated too.
- `12-terraform/02-projects` has two delivery versions side by side: Jenkins (`*/Jenkinsfile`, Helmfile) and GitHub Actions + Argo CD (`.github/workflows/` at the repo root, `bootstrap/` OIDC roles, `terraform/gitops.tf`, `app/gitops/envs/<env>/`). All GitOps resources in the Terraform project are behind `var.gitops_enabled` (default `false`, set only by the workflow), so Jenkins runs stay unchanged. Keep that split, and keep the `java-app` chart's default render identical for Helmfile. The workflows and Argo CD reference repo paths and the `main` branch.

## Running things

There are no global commands; each project documents its own in its README `## Usage`. Common patterns:

- **Ansible (15, 16):** run from the project directory, since each has its own `ansible.cfg` (sets `inventory = inventory_aws_ec2.yaml` with the `aws_ec2` dynamic inventory plugin, `host_key_checking = False`, `private_key_file`). Syntax check: `ansible-playbook <playbook>.yaml --syntax-check`. Projects usually split into `provision.yaml` / `setup-*.yaml` / `destroy*.yaml` (or `build-image-push-to-ecr.yaml` / `deploy-to-cluster.yaml` / `destroy.yaml`), with options passed via `-e` (e.g. `-e os=ubuntu`).
- **End-to-end tests:** some Ansible projects have `test-all.sh` (provision → setup → idempotency re-run → checks → destroy); its output is saved in `test.log`. These create and destroy real AWS resources.
- **Terraform (12, 15/07, 16):** per-environment `environments/<env>.tfvars` with workspaces, e.g. `terraform workspace select dev && terraform plan -var-file=environments/dev.tfvars`. Secrets come from `TF_VAR_*` env vars. Ansible playbooks in 15/07 and 16 read cluster info from `terraform output`.
- **Python (13, 14):** plain scripts using boto3/paramiko; run with `python <script>.py`.

## Secrets and state

- Secrets are never committed: they come from environment variables (e.g. `SLACK_WEBHOOK_URL`, `SMTP_PASSWORD`, `TF_VAR_mysql_root_password`), Jenkins credentials, or Kubernetes Secrets created at deploy time (Ansible tasks use `no_log: true`).
- `.gitignore` excludes `*.pem`, `*.tfstate*`, `*.tfvars`, `kubeconfig_*`, `.terraform/`, `project-vars`. Be careful: some tfstate/kubeconfig files exist on disk in project folders, and a few kubeconfig files are already tracked; don't add more.
