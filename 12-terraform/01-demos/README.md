# Module 12 – Infrastructure as Code with Terraform

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Local Setup & Providers | Install Terraform, configure the AWS provider, `terraform init` |
| 2 | Resources & Data Sources | Create a VPC and subnets, read the default VPC with a `data` block |
| 3 | Change, Destroy & More Terraform Commands | Add/remove tags, targeted destroy, `plan`, `apply -auto-approve`, full `destroy` |
| 4 | Terraform State | `terraform state list` and `state show` |
| 5 | Terraform Output | `output` blocks for the VPC and subnet IDs |
| 6 | Variables | Type constraints, `.tfvars` file, environment variables, `TF_VAR_` |
| 7 | Initialize Git Repository | Push the Terraform project to GitHub with a `.gitignore` |
| 8 | Automate AWS Infrastructure | VPC, subnet, IGW, route table, SG, EC2 with Docker + nginx, provisioners |
| 9 | Modularize Project | Split the config into files and `subnet` / `webserver` modules |
| 10 | Terraform & AWS EKS | EKS cluster with the VPC and EKS modules, deploy nginx, destroy |
| 11 | Complete CI/CD with Terraform | Jenkins pipeline: build, push, provision EC2 with Terraform, deploy |
| 12 | Configure a Shared Remote State | S3 backend for the state, used by Jenkins and locally |

## Takeaways

- **Resource vs data:** `resource` creates something, `data` reads something that already exists (e.g. `data "aws_vpc"` with `default = true`). Data is referenced as `data.<type>.<name>.id`.
- **Plan / apply / destroy:** `terraform plan` only previews, `apply -auto-approve` skips the `yes` prompt. `destroy -target <resource>` removes one resource, and Terraform warns that `-target` is not for routine use.
- **State:** `terraform state list` lists the managed resources, `terraform state show <address>` shows one resource's attributes (it needs an address).
- **Variables:** a `type` catches wrong values (a string default for a `list(string)` variable failed). Values can come from `-var-file`, from `TF_VAR_<name>` env vars, and AWS keys from `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` instead of the provider block.
- **Forced replacement:** changing `availability_zone`, `key_name` or `user_data` (with `user_data_replace_on_change = true`) recreates the resource. The plan shows `-/+` and `# forces replacement`.
- **Default resources:** `aws_default_route_table` and `aws_default_security_group` take over the route table and SG that AWS creates with the VPC, instead of creating new ones.
- **docker group in user data:** after `usermod -aG docker ec2-user`, the first SSH session still got `permission denied` on `docker ps`. A new session fixes it.
- **Provisioners:** they only run when the resource is created, so `terraform apply -replace="aws_instance.myapp-server"` was used to test them. `remote-exec` and `file` use the `connection` block, `local-exec` runs on my machine.
- **Modules:** run `terraform init` after adding a module. Inside a module use `${path.module}/entry-script.sh` for file paths, and reference module outputs as `module.<name>.<output>`.
- **EKS destroy:** the LoadBalancer created by the K8s Service is not in the Terraform state, so deleting the VPC failed with `DependencyViolation`. Cleaned up the leftover resources in the console, then `terraform destroy` again.
- **Terraform in Jenkins:** AWS keys come from Jenkins credentials as env vars, `terraform output -raw ec2_public_ip` goes into `env.EC2_PUBLIC_IP`, and the deploy stage waits 90 seconds for the server to finish its user data.
- **Remote state:** `backend "s3"` in the `terraform` block. After `terraform init` locally, `terraform state list` showed the resources Jenkins had created.

******

<details>
<summary>Local Setup & Providers</summary>
 <br />

### Demo Executed: Install Terraform and set up the AWS provider

#### Terraform Installation
Added the HashiCorp GPG key and apt repository, then installed the Terraform CLI:

    root@PC:~/modules/terraform# wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    ...
    2026-09-04 17:08:12 (171 MB/s) - written to stdout [3980/3980]
    
    root@PC:~/modules/terraform# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    deb [arch=amd64 signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com noble main
    
    root@PC:~/modules/terraform# sudo apt update && sudo apt install terraform
    ...
    Setting up terraform (1.16.1-1) ...
    
    root@PC:~/modules/terraform# terraform -v
    Terraform v1.16.1
    on linux_amd64

#### AWS Provider Configuration
`main.tf` has the AWS provider with the `eu-central-1` region and access keys, `providers.tf` pins the provider version:

    root@PC:~/modules/terraform# cat *
    provider "aws" {
        region = "eu-central-1"
        access_key = "********"
        secret_key = "********"
    }
    terraform {
      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "~> 6.0"
        }
      }
    }

#### Working Directory Initialization
`terraform init` downloaded the AWS provider and created the lock file (`.terraform.lock.hcl`). The second run added the Linode provider:

    root@PC:~/modules/terraform# terraform init
    Initializing the backend...
    
    Initializing provider plugins...
    - Finding hashicorp/aws versions matching "~> 6.0"...
    - Installing hashicorp/aws v6.63.0...
    - Installed hashicorp/aws v6.63.0 (signed by HashiCorp)
    ...
    Terraform has been successfully initialized!

    root@PC:~/modules/terraform# terraform init
    Initializing the backend...
    
    Initializing provider plugins...
    - Reusing previous version of hashicorp/aws from the dependency lock file
    - Finding linode/linode versions matching "4.4.0"...
    - Using previously-installed hashicorp/aws v6.63.0
    - Installing linode/linode v4.4.0...
    ...
    Terraform has been successfully initialized!

</details>

******

<details>
<summary>Resources & Data Sources</summary>
 <br />

### Demo Executed: Create a VPC and subnets on AWS

#### Created new VPC and Subnet in that new VPC
Created a VPC (`10.0.0.0/16`) and a subnet in it in `eu-central-1a`:

<img width="1708" height="829" alt="image" src="https://github.com/user-attachments/assets/fee6e5c5-6a75-431e-87df-98412cdfeabb" />
<img width="1704" height="823" alt="image" src="https://github.com/user-attachments/assets/172a34b8-f721-4c8e-8db6-170fcc327b72" />

`main.tf` and the apply:

```bash
    root@PC:~/modules/terraform# cat main.tf
    provider "aws" {
        region = "eu-central-1"
        access_key = "********"
        secret_key = "********"
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = "10.0.0.0/16"
    }
    
    resource "aws_subnet" "dev-subnet-1" {
        vpc_id = aws_vpc.development-vpc.id
        cidr_block = "10.0.10.0/24"
        availability_zone = "eu-central-1a"
    }

    root@PC:~/modules/terraform# terraform apply
    ...
      # aws_subnet.dev-subnet-1 will be created
      + resource "aws_subnet" "dev-subnet-1" {
          + availability_zone                              = "eu-central-1a"
          + cidr_block                                     = "10.0.10.0/24"
          ...
        }
    
      # aws_vpc.development-vpc will be created
      + resource "aws_vpc" "development-vpc" {
          + cidr_block                           = "10.0.0.0/16"
          ...
        }
    
    Plan: 2 to add, 0 to change, 0 to destroy.
    ...
      Enter a value: yes
    
    aws_vpc.development-vpc: Creating...
    aws_vpc.development-vpc: Creation complete after 2s [id=vpc-0cd62b99a8d300dd6]
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 0s [id=subnet-07584f50927802677]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

#### Created new Subnet in existing default VPC (with data)
Used a `data` block to read the default VPC and created a second subnet (`172.31.48.0/20`) in it. Running `apply` again showed no changes, so the real infrastructure matched the config.

<img width="1696" height="825" alt="image" src="https://github.com/user-attachments/assets/ace68462-cfc6-4a00-bb6b-51cc0c88d257" />

Updated `main.tf` and the two applies:

```bash
    root@PC:~/modules/terraform# cat main.tf
    provider "aws" {
        region = "eu-central-1"
        access_key = "********"
        secret_key = "********"
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = "10.0.0.0/16"
    }
    
    resource "aws_subnet" "dev-subnet-1" {
        vpc_id = aws_vpc.development-vpc.id
        cidr_block = "10.0.10.0/24"
        availability_zone = "eu-central-1a"
    }
    
    data "aws_vpc" "existing_vpc" {
        default = true
    }
    
    resource "aws_subnet" "dev-subnet-2" {
        vpc_id = data.aws_vpc.existing_vpc.id
        cidr_block = "172.31.48.0/20"
        availability_zone = "eu-central-1a"
    }
    
    root@PC:~/modules/terraform# terraform apply
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 1s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    ...
      # aws_subnet.dev-subnet-2 will be created
      + resource "aws_subnet" "dev-subnet-2" {
          + availability_zone                              = "eu-central-1a"
          + cidr_block                                     = "172.31.48.0/20"
          ...
          + vpc_id                                         = "vpc-0511d66bb75f2d673"
        }
    
    Plan: 1 to add, 0 to change, 0 to destroy.
    ...
    aws_subnet.dev-subnet-2: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-03b6a0bb1fff7080d]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    
    root@PC:~/modules/terraform# terraform apply
    ...
    No changes. Your infrastructure matches the configuration.
    
    Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
    
    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

</details>

******

<details>
<summary>Change, Destroy & More Terraform Commands</summary>
 <br />

### Demo Executed: Change and destroy resources

#### Added Tags to Existing Resources
Added `Name` tags to the VPC and subnets, and a `vpc_env` tag to the VPC. Terraform updated them in place.

<img width="1688" height="555" alt="image" src="https://github.com/user-attachments/assets/5bc7d76e-5fdb-43b3-8c0b-3ca4e09ae949" />
<img width="1692" height="545" alt="image" src="https://github.com/user-attachments/assets/e09c9e8e-de96-4862-8633-bb9e1f431589" />

`main.tf` with the tags and the apply:

    root@PC:~/modules/terraform# cat main.tf
    provider "aws" {
        region = "eu-central-1"
        access_key = "********"
        secret_key = "********"
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = "10.0.0.0/16"
        tags = {
            Name: "developnet"
            vpc_env: "dev"
        }
    }
    
    resource "aws_subnet" "dev-subnet-1" {
        vpc_id = aws_vpc.development-vpc.id
        cidr_block = "10.0.10.0/24"
        availability_zone = "eu-central-1a"
        tags = {
            Name: "subnet-1-dev"
        }
    }
    
    data "aws_vpc" "existing_vpc" {
        default = true
    }
    
    resource "aws_subnet" "dev-subnet-2" {
        vpc_id = data.aws_vpc.existing_vpc.id
        cidr_block = "172.31.48.0/20"
        availability_zone = "eu-central-1a"
        tags = {
            Name: "subnet-2-dev"
        }
    }
    
    root@PC:~/modules/terraform# terraform apply
    ...
      # aws_subnet.dev-subnet-1 will be updated in-place
      ~ resource "aws_subnet" "dev-subnet-1" {
            id                                             = "subnet-07584f50927802677"
          ~ tags                                           = {
              + "Name" = "subnet-1-dev"
            }
          ...
        }
    ...
      # aws_vpc.development-vpc will be updated in-place
      ~ resource "aws_vpc" "development-vpc" {
            id                                   = "vpc-0cd62b99a8d300dd6"
          ~ tags                                 = {
              + "Name"    = "developnet"
              + "vpc_env" = "dev"
            }
          ...
        }
    
    Plan: 0 to add, 3 to change, 0 to destroy.
    ...
    aws_subnet.dev-subnet-2: Modifications complete after 1s [id=subnet-03b6a0bb1fff7080d]
    aws_vpc.development-vpc: Modifications complete after 1s [id=vpc-0cd62b99a8d300dd6]
    ...
    aws_subnet.dev-subnet-1: Modifications complete after 1s [id=subnet-07584f50927802677]
    
    Apply complete! Resources: 0 added, 3 changed, 0 destroyed.

#### Removed Tag
Removed the `vpc_env` tag from the VPC. The plan shows it as `-> null`:

    root@PC:~/modules/terraform# terraform apply
    ...
      # aws_vpc.development-vpc will be updated in-place
      ~ resource "aws_vpc" "development-vpc" {
            id                                   = "vpc-0cd62b99a8d300dd6"
          ~ tags                                 = {
                "Name"    = "development"
              - "vpc_env" = "dev" -> null
            }
          ...
        }
    
    Plan: 0 to add, 1 to change, 0 to destroy.
    ...
    aws_vpc.development-vpc: Modifying... [id=vpc-0cd62b99a8d300dd6]
    aws_vpc.development-vpc: Modifications complete after 1s [id=vpc-0cd62b99a8d300dd6]
    
    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.

#### Destroyed a Resource
Destroyed only `dev-subnet-2` with `-target`. The rest of the resources stayed.

<img width="1912" height="483" alt="image" src="https://github.com/user-attachments/assets/ac62f14b-a414-4fda-90ce-4c1dc158852e" />

Targeted destroy, with Terraform's warning about `-target`:

    root@PC:~/modules/terraform# terraform destroy -target aws_subnet.dev-subnet-2
    ...
      # aws_subnet.dev-subnet-2 will be destroyed
      - resource "aws_subnet" "dev-subnet-2" {
          - cidr_block                                     = "172.31.48.0/20" -> null
          - id                                             = "subnet-03b6a0bb1fff7080d" -> null
          ...
        }
    
    Plan: 0 to add, 0 to change, 1 to destroy.
    ╷
    │ Warning: Resource targeting is in effect
    │
    │ You are creating a plan with the -target option, which means that the result of this plan may not represent all of the changes requested by the current configuration.
    │
    │ The -target option is not for routine use, and is provided only for exceptional situations such as recovering from errors or mistakes, or when Terraform specifically suggests to use it
    │ as part of an error message.
    ╵
    ...
    aws_subnet.dev-subnet-2: Destroying... [id=subnet-03b6a0bb1fff7080d]
    aws_subnet.dev-subnet-2: Destruction complete after 0s
    
    Destroy complete! Resources: 1 destroyed.

### Demo Executed: More Terraform commands

#### Executed Preview Command
`terraform plan` shows what would change without applying anything. Here it wants to create `dev-subnet-2` again:

    root@PC:~/modules/terraform# terraform plan
    ...
      # aws_subnet.dev-subnet-2 will be created
      + resource "aws_subnet" "dev-subnet-2" {
          + cidr_block                                     = "172.31.48.0/20"
          ...
        }
    
    Plan: 1 to add, 0 to change, 0 to destroy.
    ...
    Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.

#### Applied Config File Without Preview
`-auto-approve` skips the confirmation prompt:

    root@PC:~/modules/terraform# terraform apply -auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_subnet.dev-subnet-2: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-006d83142a1928369]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

#### Destroyed Complete Infrastructure
`terraform destroy` without a target removed everything: two subnets and the VPC.

    root@PC:~/modules/terraform# terraform destroy
    ...
      # aws_subnet.dev-subnet-1 will be destroyed
    ...
      # aws_subnet.dev-subnet-2 will be destroyed
    ...
      # aws_vpc.development-vpc will be destroyed
    ...
    Plan: 0 to add, 0 to change, 3 to destroy.
    
    Do you really want to destroy all resources?
      Terraform will destroy all your managed infrastructure, as shown above.
      There is no undo. Only 'yes' will be accepted to confirm.
    
      Enter a value: yes
    ...
    aws_vpc.development-vpc: Destruction complete after 1s
    
    Destroy complete! Resources: 3 destroyed.

</details>

******

<details>
<summary>Terraform State</summary>
 <br />

### Demo Executed: Inspect the Terraform state

#### Applied Config File Without Preview
Created the VPC and the two subnets again with `-auto-approve`:

    root@PC:~/modules/terraform# cat main.tf
    provider "aws" {
        region = "eu-central-1"
        access_key = "xxx"
        secret_key = "xxxx"
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = "10.0.0.0/16"
        tags = {
            Name: "development"
        }
    }
    
    resource "aws_subnet" "dev-subnet-1" {
        vpc_id = aws_vpc.development-vpc.id
        cidr_block = "10.0.10.0/24"
        availability_zone = "eu-central-1a"
        tags = {
            Name: "subnet-1-dev"
        }
    }
    
    data "aws_vpc" "existing_vpc" {
        default = true
    }
    
    resource "aws_subnet" "dev-subnet-2" {
        vpc_id = data.aws_vpc.existing_vpc.id
        cidr_block = "172.31.48.0/20"
        availability_zone = "eu-central-1a"
        tags = {
            Name: "subnet-2-default"
        }
    }
    
    root@PC:~/modules/terraform# terraform apply -auto-approve
    ...
      # aws_subnet.dev-subnet-1 will be created
    ...
      # aws_subnet.dev-subnet-2 will be created
    ...
      # aws_vpc.development-vpc will be created
    ...
    Plan: 3 to add, 0 to change, 0 to destroy.
    aws_subnet.dev-subnet-2: Creating...
    aws_vpc.development-vpc: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-0f84f579e64b837ff]
    aws_vpc.development-vpc: Creation complete after 1s [id=vpc-047ff10c7a5f9ab73]
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 1s [id=subnet-0bd0a41afd6671e9d]
    
    Apply complete! Resources: 3 added, 0 changed, 0 destroyed.

#### Inspected Terraform State
`terraform state list` lists the resources in the state, `terraform state show` shows the attributes of one of them (it fails without an address):

    root@PC:~/modules/terraform# terraform state
    Usage: terraform [global options] state <subcommand> [options] [args]
    ...
    Subcommands:
        identities      List the identities of resources in the state
        list            List resources in the state
        mv              Move an item in the state
        pull            Pull current state and output to stdout
        push            Update remote state from a local state file
        replace-provider    Replace provider in the state
        rm              Remove instances from the state
        show            Show a resource in the state
    
    root@PC:~/modules/terraform# terraform state list
    data.aws_vpc.existing_vpc
    aws_subnet.dev-subnet-1
    aws_subnet.dev-subnet-2
    aws_vpc.development-vpc
    
    root@PC:~/modules/terraform# terraform state show
    ╷
    │ Error: Required argument missing
    │
    │ Exactly one argument expected: the address of a resource instance to show.
    ╵
    
    root@PC:~/modules/terraform# terraform state show aws_subnet.dev-subnet-1
    # aws_subnet.dev-subnet-1:
    resource "aws_subnet" "dev-subnet-1" {
        arn                                            = "arn:aws:ec2:eu-central-1:731872836472:subnet/subnet-0bd0a41afd6671e9d"
        assign_ipv6_address_on_creation                = false
        availability_zone                              = "eu-central-1a"
        availability_zone_id                           = "euc1-az2"
        cidr_block                                     = "10.0.10.0/24"
        ...
        id                                             = "subnet-0bd0a41afd6671e9d"
        ...
        owner_id                                       = "731872836472"
        private_dns_hostname_type_on_launch            = "ip-name"
        region                                         = "eu-central-1"
        tags                                           = {
            "Name" = "subnet-1-dev"
        }
        tags_all                                       = {
            "Name" = "subnet-1-dev"
        }
        vpc_id                                         = "vpc-047ff10c7a5f9ab73"
    }

</details>

******

<details>
<summary>Terraform Output</summary>
 <br />

### Demo Executed: Print resource IDs with output values

#### Defined Output Values in Configuration
Added two `output` blocks to print the VPC ID and the subnet ID after apply:

```bash
    root@PC:~/modules/terraform# cat main.tf
    provider "aws" {
        region = "eu-central-1"
        access_key = "xxx"
        secret_key = "xxx"
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = "10.0.0.0/16"
        tags = {
            Name: "development"
        }
    }
    
    resource "aws_subnet" "dev-subnet-1" {
        vpc_id = aws_vpc.development-vpc.id
        cidr_block = "10.0.10.0/24"
        availability_zone = "eu-central-1a"
        tags = {
            Name: "subnet-1-dev"
        }
    }
    
    output "dev-vpc-id"{
        value = aws_vpc.development-vpc.id
    }
    
    output "dev-subnet-id"{
        value = aws_subnet.dev-subnet-1.id
    }
```

#### Applied Configuration and Extracted Outputs
The plan lists the outputs under "Changes to Outputs", and the real IDs are printed at the end:

```bash
    root@PC:~/modules/terraform# terraform apply --auto-approve
    ...
      # aws_subnet.dev-subnet-1 will be created
    ...
      # aws_vpc.development-vpc will be created
    ...
    Plan: 2 to add, 0 to change, 0 to destroy.
    
    Changes to Outputs:
      + dev-subnet-id = (known after apply)
      + dev-vpc-id    = (known after apply)
    aws_vpc.development-vpc: Creating...
    aws_vpc.development-vpc: Creation complete after 2s [id=vpc-0e7925ca7de335498]
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 0s [id=subnet-0ee36142d5bbbb3de]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
    
    Outputs:
    
    dev-subnet-id = "subnet-0ee36142d5bbbb3de"
    dev-vpc-id = "vpc-0e7925ca7de335498"
```

</details>

******

<details>
<summary>Variables</summary>
 <br />

### Demo Executed: Use variables instead of hardcoded values

#### Restricted Value of Variable by Defining a Type
Gave `cidr_blocks` the type `list(string)`. The default value was still a single string, so Terraform rejected it:

```bash
    root@PC:~/modules/terraform# cat terraform-dev.tfvars
    cidr_blocks = ["10.0.0.0/16", "10.0.10.0/24"]
    
    root@PC:~/modules/terraform# terraform apply -var-file terraform-dev.tfvars
    ╷
    │ Error: Invalid default value for variable
    │
    │   on main.tf line 9, in variable "cidr_blocks":
    │    9:     default = "10.0.10.0/24"
    │
    │ This default value is not compatible with the variable's type constraint: list of string required, but have
    │ string.
    ╵
```

#### Passed Variables in Multiple Ways (Files & Environments)
Changed the variable to a `list(object)` with `cidr_block` and `name`, and passed the values from `terraform-dev.tfvars` with `-var-file`. The VPC uses `var.cidr_blocks[0]`, the subnet uses `var.cidr_blocks[1]`:

```bash
    root@PC:~/modules/terraform# cat main.tf
    ...
    
    variable "cidr_blocks" {
        description = "cidr blocks for vps and subnets"
        type = list(object({
            cidr_block = string
            name = string
        }))
    }
    
    resource "aws_vpc" "development-vpc" {
        cidr_block = var.cidr_blocks[0].cidr_block
        tags = {
            Name: var.cidr_blocks[0].name
        }
    }
    ...
    
    root@PC:~/modules/terraform# cat terraform-dev.tfvars
    cidr_blocks = [
        {cidr_block = "10.0.0.0/16", name = "dev-vpc"},
        {cidr_block ="10.0.10.0/24", name = "dev-subent"}
    ]
    
    root@PC:~/modules/terraform# terraform apply -var-file terraform-dev.tfvars
    ...
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 0s [id=subnet-0210999dc3fc7fc4b]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

#### Used Environment Variables to Extract AWS Credentials
Removed the access keys from the provider block and exported them as environment variables instead:

```bash
    root@PC:~/modules/terraform# export AWS_SECRET_ACCESS_KEY=xxx
    root@PC:~/modules/terraform# export AWS_ACCESS_KEY_ID=xxx
    
    root@PC:~/modules/terraform# terraform apply -var-file terraform-dev.tfvars
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0e7925ca7de335498]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-0210999dc3fc7fc4b]
    
    Terraform used the selected providers to generate the following execution plan...
    Plan: 0 to add, 2 to change, 0 to destroy.
```

#### Set Variable Using TF_VAR_name Environment Variable
Set the availability zone with a `TF_VAR_` environment variable. Changing it from `eu-central-1a` to `eu-central-1b` forced Terraform to replace the subnet, without touching any file:

```bash
    root@PC:~/modules/terraform# export TF_VAR_availability_zone="eu-central-1a"
    root@PC:~/modules/terraform# terraform apply -var-file terraform-dev.tfvars
    ...
    No changes. Your infrastructure matches the configuration.
    
    root@PC:~/modules/terraform# export TF_VAR_availability_zone="eu-central-1b"
    root@PC:~/modules/terraform# terraform apply -var-file terraform-dev.tfvars
    ...
      # aws_subnet.dev-subnet-1 must be replaced
    -/+ resource "aws_subnet" "dev-subnet-1" {
          ~ arn                                            = "arn:aws:ec2:eu-central-1:731872836472:subnet/subnet-0210999dc3fc7fc4b" -> (known after apply)
          ~ availability_zone                              = "eu-central-1a" -> "eu-central-1b" # forces replacement
    ...
    aws_subnet.dev-subnet-1: Destroying... [id=subnet-0210999dc3fc7fc4b]
    aws_subnet.dev-subnet-1: Destruction complete after 1s
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 1s [id=subnet-0ac4e9b5390417f7b]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

</details>

******

<details>
<summary>Initialize Git Repository</summary>
 <br />

Created the Git repo and pushed it to GitHub. The second `git status` is after adding a `.gitignore`: `.terraform/`, the state files and the `.tfvars` file are no longer listed.

```bash
root@PC:~/modules/terraform# git init
...
Initialized empty Git repository in /root/modules/terraform/.git/
root@PC:~/modules/terraform# git remote add origin https://github.com/emrearabacioglu/terraform.git
root@PC:~/modules/terraform# git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .terraform.lock.hcl
        .terraform/
        main.tf
        providers.tf
        terraform-dev.tfvars
        terraform.tfstate
        terraform.tfstate.backup

nothing added to commit but untracked files present (use "git add" to track)
root@PC:~/modules/terraform# git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore
        .terraform.lock.hcl
        main.tf
        providers.tf

nothing added to commit but untracked files present (use "git add" to track)
root@PC:~/modules/terraform# git add .
root@PC:~/modules/terraform# git commit -m "initial"
[master (root-commit) dd3d558] initial
...
 4 files changed, 97 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 .terraform.lock.hcl
 create mode 100644 main.tf
 create mode 100644 providers.tf
root@PC:~/modules/terraform# git push -u origin master
...
To https://github.com/emrearabacioglu/terraform.git
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.
```

</details>

******

<details>
<summary>Demo Project: Automate AWS Infrastructure</summary>
 <br />

### Demo Executed: Part 1 – VPC, subnet, routing and security group

#### Created VPC & Subnet
Created a new VPC and subnet with values from variables. The resources from the earlier demos were destroyed in the same apply.

`main.tf` and the apply:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    provider "aws" {
        region = "eu-central-1"
    }
    
    variable vpc_cidr_block {}
    variable subnet_cidr_block {}
    variable avail_zone {}
    variable env_prefix {}
    
    resource "aws_vpc" "myapp-vpc" {
        cidr_block = var.vpc_cidr_block
        tags = {
            Name: "${var.env_prefix}-vpc"
        }
    }
    
    resource "aws_subnet" "myapp-subnet-1" {
        vpc_id = aws_vpc.myapp-vpc.id
        cidr_block = var.subnet_cidr_block
        availability_zone = var.avail_zone
        tags = {
            Name: "${var.env_prefix}-subnet-1"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 2 to add, 0 to change, 2 to destroy.
    aws_subnet.dev-subnet-1: Destroying... [id=subnet-0ac4e9b5390417f7b]
    aws_vpc.myapp-vpc: Creating...
    aws_subnet.dev-subnet-1: Destruction complete after 1s
    aws_vpc.development-vpc: Destroying... [id=vpc-0e7925ca7de335498]
    aws_vpc.development-vpc: Destruction complete after 0s
    aws_vpc.myapp-vpc: Creation complete after 1s [id=vpc-01cb698649ba9cb82]
    aws_subnet.myapp-subnet-1: Creating...
    aws_subnet.myapp-subnet-1: Creation complete after 1s [id=subnet-0d0c73d53c8304752]
    
    Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```
<img width="1704" height="835" alt="image" src="https://github.com/user-attachments/assets/34e98593-d13c-4717-97f0-5cfa558504ae" />

<img width="1702" height="809" alt="image" src="https://github.com/user-attachments/assets/5e103ddf-82a3-4749-ad35-175f51f76661" />

#### Created custom Route Table
Created an Internet Gateway and a route table with a `0.0.0.0/0` route to it:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_route_table" "myapp-route-table" {
        vpc_id = aws_vpc.myapp-vpc.id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-rtb"
        }
    }
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = aws_vpc.myapp-vpc.id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 2 to add, 0 to change, 0 to destroy.
    aws_internet_gateway.myapp-igw: Creating...
    aws_internet_gateway.myapp-igw: Creation complete after 1s [id=igw-0cdf26ec1de16018d]
    aws_route_table.myapp-route-table: Creating...
    aws_route_table.myapp-route-table: Creation complete after 1s [id=rtb-0ecdf898f49754b61]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```
<img width="1710" height="833" alt="image" src="https://github.com/user-attachments/assets/379b2d17-18cd-4ca7-8d85-e17488fdc22a" />

#### Added Subnet Association with Route Table
Associated the subnet with the new route table using `aws_route_table_association`:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_route_table_association" "a-rtb-subnet" {
        subnet_id = aws_subnet.myapp-subnet-1.id
        route_table_id = aws_route_table.myapp-route-table.id
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_route_table_association.a-rtb-subnet: Creating...
    aws_route_table_association.a-rtb-subnet: Creation complete after 0s [id=rtbassoc-07c4ac24965795e66]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1694" height="825" alt="image" src="https://github.com/user-attachments/assets/5f640689-588d-4002-8acb-8b06a15fca59" />

#### Configured Default/Main Route Table
Then switched to the route table AWS creates with the VPC. Commented out the custom route table and the association, and added the IGW route to the main route table with `aws_default_route_table`:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    /* Custom Route Table commented out */
    
    resource "aws_default_route_table" "main-rtb" {
        default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-main-rtb"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_default_route_table.main-rtb: Creating...
    aws_default_route_table.main-rtb: Creation complete after 0s [id=rtb-002936ab76ff4961e]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1710" height="825" alt="image" src="https://github.com/user-attachments/assets/8e641332-408b-4a32-83cd-b26b83318f72" />

#### Created Security Group
Created a security group: SSH (22) only from my IP, 8080 open to everyone, all outbound traffic allowed:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_security_group" "myapp-sg" {
        name = "myapp-sg"
        vpc_id = aws_vpc.myapp-vpc.id
    
        ingress{
            from_port = 22
            to_port = 22
            protocol = "TCP"
            cidr_blocks = [var.my_ip]
        }
    
        ingress{
            from_port = 8080
            to_port = 8080
            protocol = "TCP"
            cidr_blocks = ["0.0.0.0/0"]
        }
    
        egress{
            from_port = 0
            to_port = 0
            protocol = "-1"
            cidr_blocks = ["0.0.0.0/0"]
            prefix_list_ids = []
        }
    
        tags = {
            Name: "${var.env_prefix}-sg"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_security_group.myapp-sg: Creating...
    aws_security_group.myapp-sg: Creation complete after 3s [id=sg-04a0b7384ea23fdfc]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```
<img width="1704" height="635" alt="image" src="https://github.com/user-attachments/assets/664faf91-0c84-4953-8f86-5ebf540fe328" />

#### Configured Default Security Group
Same idea as the route table: replaced the custom SG with `aws_default_security_group`, using the same rules.

<img width="1708" height="701" alt="image" src="https://github.com/user-attachments/assets/5e46d969-e203-46c8-a0b3-878d8277420d" />

The apply destroys the custom SG and takes over the default one:

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    aws_security_group.myapp-sg: Destroying... [id=sg-04a0b7384ea23fdfc]
    aws_default_security_group.default-sg: Creating...
    aws_security_group.myapp-sg: Destruction complete after 1s
    aws_default_security_group.default-sg: Creation complete after 2s [id=sg-0bc899b0d94188f99]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

### Demo Executed: Part 2 – EC2 instance and SSH key pair

#### Created EC2 Instance (Manual Key Pair Approach)
First created a `t2.micro` instance with a key pair I made in the AWS console (`server-key-pair.pem`). Restricted the key permissions, then applied:

```bash
    root@PC:~/modules/terraform (feature/EC2)# ls ~/.ssh/server-key-pair.pem
    /root/.ssh/server-key-pair.pem
    root@PC:~/modules/terraform (feature/EC2)# chmod 400 ~/.ssh/server-key-pair.pem
    root@PC:~/modules/terraform (feature/EC2)# ls -l ~/.ssh/server-key-pair.pem
    -r-------- 1 root root 1678 Sep  5 21:00 /root/.ssh/server-key-pair.pem

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Creation complete after 13s [id=i-06ca00864feabd5a8]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

#### SSH into EC2 Instance (Manual Key)
Connected to the new Amazon Linux 2023 server with the downloaded `.pem` key:

```bash
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/server-key-pair.pem ec2-user@18.192.8.225
    The authenticity of host '18.192.8.225 (18.192.8.225)' can't be established.
    ED25519 key fingerprint is SHA256:4jQZsvFbwQg80vSiK0YNniKkZj3t/In4CCjv2qZr1AI.
    This key is not known by any other names.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    Warning: Permanently added '18.192.8.225' (ED25519) to the list of known hosts.
    ...
    [ec2-user@ip-10-0-10-185 ~]$ exit
    logout
    Connection to 18.192.8.225 closed.
```

#### Configured SSH Key Pair in Terraform Config File
To skip the console step, added an `aws_key_pair` resource that uses my local public key (`id_rsa.pub`). The AMI comes from a `data "aws_ami"` block (latest Amazon Linux 2023):

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    
    data "aws_ami" "latest-amazon-linux-image" {
        most_recent = true
        owners = ["amazon"]
        filter {
            name = "name"
            values = ["al2023-ami-2023.*-x86_64"]
        }
        filter{
            name = "virtualization-type"
            values = ["hvm"]
        }
    }
    
    resource "aws_key_pair" "ssh-key" {
        key_name = "server-key"
        public_key = file(var.public_key_location)
    }
    
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
```

#### Created EC2 Instance (Automated Key Pair)
The new `key_name` forces replacement, so Terraform destroyed the instance and created a new one with the new key:

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server must be replaced
    -/+ resource "aws_instance" "myapp-server" {
    ...
          ~ key_name                             = "server-key-pair" -> "server-key" # forces replacement
    ...
      # aws_key_pair.ssh-key will be created
      + resource "aws_key_pair" "ssh-key" {
          + key_name        = "server-key"
          + public_key      = "ssh-rsa AAAAB3NzaC1yc...[TRUNCATED]...root@PC"
    ...
    Plan: 2 to add, 0 to change, 1 to destroy.
    aws_instance.myapp-server: Destroying... [id=i-06ca00864feabd5a8]
    aws_instance.myapp-server: Destruction complete after 20s
    aws_key_pair.ssh-key: Creating...
    aws_key_pair.ssh-key: Creation complete after 0s [id=server-key]
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Creation complete after 13s [id=i-03ad6fbe423be3bde]
    
    Apply complete! Resources: 2 added, 0 changed, 1 destroyed.
```

#### SSH into EC2 Instance (Automated Key)
Got the public IP (`35.157.195.225`) from `terraform state show`, then connected with `id_rsa`. It also works without `-i`, because `id_rsa` is the default key. After that I deleted the old `.pem` key.

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform state show aws_instance.myapp-server
    ...
    
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/id_rsa ec2-user@35.157.195.225
    ...
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@35.157.195.225
    ...
    Last login: Sat Sep  5 18:22:33 2026 from <my-ip>
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# rm ~/.ssh/server-key-pair.pem
```
<img width="1905" height="927" alt="image" src="https://github.com/user-attachments/assets/0db12caa-d5f5-477e-aaec-b77d1ef9698c" />
<img width="1909" height="404" alt="image" src="https://github.com/user-attachments/assets/70dd2aec-28e6-4274-a35b-bfe648b36bd6" />

### Demo Executed: Part 3 – Install Docker and run nginx with user data

#### Configured Terraform to install Docker and run nginx image
Added `user_data` to the instance: update the OS, install and start Docker, add `ec2-user` to the docker group and run nginx on port 8080. In the first SSH session `docker ps` got `permission denied`, because the group change only applies to a new session. After reconnecting, the nginx container was running.

```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server must be replaced
    -/+ resource "aws_instance" "myapp-server" {
    ...
      + user_data                            = <<-EOT # forces replacement
            #!/bin/bash
            sudo yum update -y && sudo yum install docker -y
            sudo systemctl start docker
            sudo usermod -aG docker ec2-user
            docker run -d -p 8080:80 nginx
        EOT
    ...
      ~ user_data_replace_on_change          = false -> true
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    ...
    aws_instance.myapp-server: Creation complete after 13s [id=i-0839b33e99a21adc8]
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    ec2_public_ip = "18.198.22.100"

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@18.198.22.100
    ...
    [ec2-user@ip-10-0-10-74 ~]$ docker ps
    permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.44/containers/json": dial unix /var/run/docker.sock: connect: permission denied
    [ec2-user@ip-10-0-10-74 ~]$ exit
    logout
    Connection to 18.198.22.100 closed.

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@18.198.22.100
    ...
    [ec2-user@ip-10-0-10-74 ~]$ docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                   NAMES
    0fcfec58c119   nginx     "/docker-entrypoint.…"   58 seconds ago   Up 56 seconds   0.0.0.0:8080->80/tcp, :::8080->80/tcp   jovial_hopper
```

#### Extract shell commands to own shell script
Moved the user data commands into `entry-script.sh` and loaded it with `file()`. Applied again and checked the container on the new instance:

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat entry-script.sh
    #!/bin/bash
    sudo yum update -y && sudo yum install docker -y
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
    docker run -d -p 8080:80 nginx

    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        user_data = file("entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }

    root@PC:~/modules/terraform (feature/EC2)# terraform apply --auto-approve
    ...
    Plan: 1 to add, 0 to change, 1 to destroy.
    ...
    aws_instance.myapp-server: Creation complete after 12s [id=i-0c8ebfbd84376417c]
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    ec2_public_ip = "3.79.21.47"

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@3.79.21.47
    ...
    [ec2-user@ip-10-0-10-134 ~]$ exit
    logout
    Connection to 3.79.21.47 closed.

    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@3.79.21.47
    ...
    [ec2-user@ip-10-0-10-134 ~]$ docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                   NAMES
    a25a61191afb   nginx     "/docker-entrypoint.…"   39 seconds ago   Up 37 seconds   0.0.0.0:8080->80/tcp, :::8080->80/tcp   pedantic_wiles
```

#### Accessed nginx through Browser
Opened the nginx page in the browser with the instance's public IP on port 8080:

<img width="1344" height="315" alt="image" src="https://github.com/user-attachments/assets/348edfb5-4007-419a-9f96-7bf693536620" />

### Demo Executed: Provisioners

#### Used “remote-exec” provisioner
Ran an inline command on the new instance with `remote-exec`. Provisioners only run when the resource is created, so I used `-replace` to recreate the instance. Terraform connected over SSH and the command created `newdir`, which I checked with a manual SSH session:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# terraform apply -replace="aws_instance.myapp-server"
    ...
    Terraform will perform the following actions:
    
      # aws_instance.myapp-server will be replaced, as requested
    -/+ resource "aws_instance" "myapp-server" {
    ...
    aws_instance.myapp-server: Destroying... [id=i-0c8ebfbd84376417c]
    aws_instance.myapp-server: Destruction complete after 30s
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Provisioning with 'remote-exec'...
    aws_instance.myapp-server (remote-exec): Connecting to remote host via SSH...
    aws_instance.myapp-server (remote-exec):   Host: 18.199.152.174
    aws_instance.myapp-server (remote-exec):   User: ec2-user
    aws_instance.myapp-server (remote-exec):   Password: false
    aws_instance.myapp-server (remote-exec):   Private key: true
    ...
    aws_instance.myapp-server (remote-exec): Connected!
    aws_instance.myapp-server: Creation complete after 19s [id=i-0cd8a7993b65908ea]
    
    Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
    
    Outputs:
    aws_ami_id = "ami-030f85e68f5db92a9"
    ec2_public_ip = "18.199.152.174"

    root@PC:~/modules/terraform (feature/provisioners)# ssh ec2-user@18.199.152.174
    ...
    [ec2-user@ip-10-0-10-131 ~]$ ls
    newdir
    [ec2-user@ip-10-0-10-131 ~]$ exit
    logout
    Connection to 18.199.152.174 closed.
```

#### Used “file” provisioner
The `file` provisioner copies `entry-script.sh` from my machine to the `ec2-user` home directory on the server, so no manual `scp` is needed. The `connection` block tells Terraform how to SSH in:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
    ...
        connection {
            type = "ssh"
            host = self.public_ip
            user = "ec2-user"
            private_key = file(var.private_key_location)
        }
    
        provisioner "file" {
            source = "entry-script.sh"
            destination = "/home/ec2-user/entry-script-on-ec2.sh"
        }
    ...
```

#### Used “local-exec” provisioner
`local-exec` runs on my machine, not on the server. Here it writes the instance's public IP to `output.txt`. `remote-exec` with `script` runs the uploaded script on the server:

```bash
    root@PC:~/modules/terraform (feature/provisioners)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
    ...
        provisioner "remote-exec" {
            script = "entry-script.sh"
        }
    
        provisioner "local-exec" {
            command = "echo ${self.public_ip} > output.txt"
        }
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
```

</details>

******

<details>
<summary>Demo Project: Modularize Project</summary>
 <br />

### Demo Executed: Split the configuration into modules

#### Extracted output values, variables and providers into its own file
Moved the outputs to `outputs.tf`, the variables to `variables.tf` and the provider requirements to `providers.tf`:

```bash
    root@PC:~/modules/terraform (feature/modules)# cat outputs.tf
    output "aws_ami_id" {
        value = data.aws_ami.latest-amazon-linux-image.id
    }
    
    output "ec2_public_ip" {
        value = aws_instance.myapp-server.public_ip
    }

    root@PC:~/modules/terraform (feature/modules)# cat providers.tf
    terraform {
      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "~> 6.0"
        }
        linode = {
          source  = "linode/linode"
          version = "4.4.0"
        }
      }
    }

    root@PC:~/modules/terraform (feature/modules)# cat variables.tf
    variable vpc_cidr_block {}
    variable subnet_cidr_block{}
    variable avail_zone {}
    variable env_prefix {}
    variable my_ip{}
    variable instance_type{}
    variable public_key_location{}
```

#### Created subnet module and used it in root config file
Moved the subnet, internet gateway and route table into `modules/subnet`. The root `main.tf` calls the module and passes the variables it needs:

```bash
    root@PC:~/modules/terraform/modules/subnet (feature/modules)# cat main.tf
    resource "aws_subnet" "myapp-subnet-1" {
        vpc_id = var.vpc_id
        cidr_block = var.subnet_cidr_block
        availability_zone = var.avail_zone
        tags = {
            Name: "${var.env_prefix}-subnet-1"
        }
    }
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = var.vpc_id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }
    
    resource "aws_default_route_table" "main-rtb" {
        default_route_table_id = var.default_route_table_id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-main-rtb"
        }
    }

    root@PC:~/modules/terraform (feature/modules)# cat main.tf
    ...
    module "myapp-subnet" {
        source = "./modules/subnet"
        subnet_cidr_block = var.subnet_cidr_block
        avail_zone = var.avail_zone
        env_prefix = var.env_prefix
        vpc_id = aws_vpc.myapp-vpc.id
        default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
    }
    ...
```

#### Created webserver module and used it in root config file
Moved the security group, AMI data source, key pair and EC2 instance into `modules/webserver`. The root config passes the `subnet_id` from the subnet module's output. Fixed two errors on the way: missing `=` signs in block definitions, and the `user_data` path, which now uses `${path.module}`.

```bash
    root@PC:~/modules/terraform/modules/webserver (feature/modules)# cat main.tf
    ...
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = var.subnet_id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = aws_key_pair.ssh-key.key_name
    
        user_data = file("${path.module}/entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }

    root@PC:~/modules/terraform (feature/modules)# cat main.tf
    ...
    module "myapp-server" {
        source = "./modules/webserver"
        vpc_id = aws_vpc.myapp-vpc.id
        my_ip = var.my_ip
        env_prefix = var.env_prefix
        image_name = var.image_name
        public_key_location = var.public_key_location
        instance_type = var.instance_type
        subnet_id = module.myapp-subnet.subnet.id
        avail_zone = var.avail_zone
    }
```

#### terraform init and apply
Ran `terraform init` again to load the modules. The apply destroyed the old root-level resources and created them again inside the modules. Docker was installed on the new server:

```bash
    root@PC:~/modules/terraform (feature/modules)# terraform init
    Initializing the backend...
    
    Initializing modules...
    - myapp-server in modules/webserver
    - myapp-subnet in modules/subnet
    ...
    Terraform has been successfully initialized!

    root@PC:~/modules/terraform (feature/modules)# terraform apply --auto-approve
    ...
    module.myapp-server.aws_instance.myapp-server: Creating...
    module.myapp-server.aws_instance.myapp-server: Creation complete after 13s [id=i-015b96172c33e1907]
    aws_instance.myapp-server: Destruction complete after 20s
    ...
    Apply complete! Resources: 3 added, 0 changed, 2 destroyed.
    
    Outputs:
    ec2_public_ip = "63.183.197.82"

    root@PC:~/modules/terraform (feature/modules)# ssh ec2-user@63.183.197.82
    ...
    [ec2-user@ip-10-0-10-239 ~]$ docker -v
    Docker version 25.0.14, build 0bab007
```

</details>

******

<details>
<summary>Demo Project: Terraform & AWS EKS</summary>
 <br />

### Demo Executed: Create an EKS cluster with Terraform and deploy nginx

#### Created the VPC by using the VPC module
Used the `terraform-aws-modules/vpc/aws` module: public and private subnets across multiple AZs, one NAT gateway, and the `kubernetes.io/...` tags that the cluster and load balancers need:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat vpc.tf
    ...
    module "myapp-vpc" {
      source  = "terraform-aws-modules/vpc/aws"
      version = "6.7.2"
    
      name = "myapp-vpc"
      cidr = var.vpc_cidr_block
      private_subnets = var.private_subnet_cidr_blocks
      public_subnets = var.public_subnet_cidr_blocks
      azs = data.aws_availability_zones.azs.names
    
      enable_nat_gateway = true
      single_nat_gateway = true
      enable_dns_hostnames = true
    
      tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
      }
    
      public_subnet_tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
        "kubernetes.io/role/elb" = 1
      }
    
      private_subnet_tags = {
        "kubernetes.io/cluster/myapp-eks-cluster" = "shared"
        "kubernetes.io/role/internal-elb" = 1
      }
    }
```

#### Created the EKS cluster and worker nodes by using the EKS module
Used the `terraform-aws-modules/eks/aws` module. The cluster runs in the private subnets of the VPC above, with a managed node group `dev` of `t2.small` instances. Cluster creator admin permissions are enabled and the CoreDNS, kube-proxy and vpc-cni add-ons are added:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat eks-cluster.tf
    module "eks" {
      source  = "terraform-aws-modules/eks/aws"
      version = "21.25.0"
    
      name = "myapp-eks-cluster"
      kubernetes_version = "1.33"
    
      subnet_ids = module.myapp-vpc.private_subnets
      vpc_id = module.myapp-vpc.vpc_id
    
      endpoint_public_access = true
      enable_cluster_creator_admin_permissions = true
    ...
      eks_managed_node_groups = {
        dev = {
          ami_type       = "AL2023_x86_64_STANDARD"
          instance_types = ["t2.small"]
    
          min_size     = 1
          max_size     = 3
          desired_size = 3
        }
      }
    }
```

#### Applied configurations
After `terraform init`, the apply created 62 resources (VPC, subnets, NAT gateway, EKS cluster, node group, IAM roles and more). The cluster alone took about 8 minutes:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform apply --auto-approve
    ...
    module.eks.aws_eks_cluster.this[0]: Creation complete after 7m55s [id=myapp-eks-cluster]
    ...
    module.eks.module.eks_managed_node_group["dev"].aws_eks_node_group.this[0]: Creation complete after 1m48s [id=myapp-eks-cluster:dev-f0cb57967fd66cb58d0c4e27ff]
    ...
    Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
```
<img width="1706" height="831" alt="image" src="https://github.com/user-attachments/assets/dbcea9c7-e5ad-4f9e-b3a4-1af38ece890f" />
<img width="1708" height="515" alt="image" src="https://github.com/user-attachments/assets/3043e9b5-37f3-4fee-a4e7-7fd7dd185810" />
<img width="1700" height="371" alt="image" src="https://github.com/user-attachments/assets/0896ec69-bf4f-401c-adfe-fd96fe6aaf43" />
<img width="1708" height="727" alt="image" src="https://github.com/user-attachments/assets/bd721718-a254-4f6d-85fe-d2696a0a3a98" />
<img width="1708" height="819" alt="image" src="https://github.com/user-attachments/assets/083dfc5d-48fe-4cd8-b814-58958950c30e" />
<img width="1698" height="819" alt="image" src="https://github.com/user-attachments/assets/258e0495-3f51-4112-8f05-e3a2d68d84e8" />

#### Connected kubectl to the Cluster
Updated the local kubeconfig with the AWS CLI and checked that the three nodes are `Ready`:

```bash
    root@PC:~/modules/terraform (feature/eks)# aws eks update-kubeconfig --name myapp-eks-cluster --region eu-central-1
    Added new context arn:aws:eks:eu-central-1:731872836472:cluster/myapp-eks-cluster to /root/.kube/config
    
    root@PC:~/modules/terraform (feature/eks)# kubectl get node
    NAME                                          STATUS   ROLES    AGE   VERSION
    ip-10-0-1-175.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
    ip-10-0-2-147.eu-central-1.compute.internal   Ready    <none>   50m   v1.33.13-eks-cb19647
    ip-10-0-3-48.eu-central-1.compute.internal    Ready    <none>   50m   v1.33.13-eks-cb19647
```

#### Deployed nginx Application/Pod
Deployed nginx with a Deployment (2 replicas) and a Service of type `LoadBalancer`, then got the load balancer's DNS name from `kubectl get svc`:

```bash
    root@PC:~/modules/terraform (feature/eks)# cat nginx-config.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
      namespace: dev
      labels:
        app: nginx
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: nginx
          profile: fargate
      template:
        metadata:
          labels:
            app: nginx
            profile: fargate
        spec:
          containers:
          - name: nginx
            image: nginx
            ports:
            - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      ports:
      - name: http
        port: 80
        protocol: TCP
        targetPort: 80
      selector:
        app: nginx
      type: LoadBalancer

    root@PC:~/modules/terraform (feature/eks)# kubectl apply -f./nginx-config.yaml
    deployment.apps/nginx created
    service/nginx configured

    root@PC:~/modules/terraform (feature/eks)# kubectl get pod
    NAME                     READY   STATUS    RESTARTS   AGE
    nginx-86c57bc6b8-mxkbd   1/1     Running   0          12s
    
    root@PC:~/modules/terraform (feature/eks)# kubectl get svc
    NAME         TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
    kubernetes   ClusterIP      172.20.0.1     <none>                                                                   443/TCP        71m
    nginx        LoadBalancer   172.20.3.243   a9e4950619e104317bd888cf6839b22f-825226598.eu-central-1.elb.amazonaws.com   80:31956/TCP   12m
```

<img width="1708" height="807" alt="image" src="https://github.com/user-attachments/assets/7641e6f9-83de-4142-a6e2-9431e78cd34c" />
<img width="1708" height="401" alt="image" src="https://github.com/user-attachments/assets/ecbc4483-dd23-4fb1-84d2-3a8967b43242" />

#### Terraform destroy
The first `terraform destroy` got stuck on the VPC. The load balancer and network interfaces created by Kubernetes are not in the Terraform state, so AWS refused to delete the VPC with `DependencyViolation`:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform destroy
    ...
    module.myapp-vpc.aws_vpc.this[0]: Still destroying... [id=vpc-0436e4eb7b3668acb, 12m52s elapsed]
    ^C
    Interrupt received.
    ...
    Error: deleting EC2 VPC (vpc-0436e4eb7b3668acb): operation error EC2: DeleteVpc, https response error StatusCode: 400, RequestID: 2105439e-1511-4369-bed0-736ad2d3ca2f, api error DependencyViolation: The vpc 'vpc-0436e4eb7b3668acb' has dependencies and cannot be deleted.
```

Deleted the leftover resources in the AWS console, then ran `terraform destroy` again. Nothing was left and the state is empty:

```bash
    root@PC:~/modules/terraform (feature/eks)# terraform destroy --auto-approve
    ...
    No changes. No objects need to be destroyed.
    Either you have not created any objects yet or the existing objects were already deleted outside of Terraform.
    Destroy complete! Resources: 0 destroyed.
    
    root@PC:~/modules/terraform (feature/eks)# terraform state list
    root@PC:~/modules/terraform (feature/eks)#
```

</details>

******

<details>
<summary>Demo Project: Complete CI/CD with Terraform</summary>
 <br />

### Demo Executed: Jenkins pipeline that provisions the server with Terraform and deploys to it

#### Created SSH key pair for EC2 Instance
Created the `myapp-key-pair` key pair in AWS. Jenkins uses it to SSH into the new server.

<img width="1900" height="393" alt="image" src="https://github.com/user-attachments/assets/39bcd1a4-63ea-43cc-b4e9-7d01332bcfa8" />

#### Created Credential in Jenkins
Added the credentials the pipeline needs in Jenkins: AWS access keys for Terraform, Docker Hub login, and the EC2 SSH private key.

#### Installed Terraform inside Jenkins Container
Installed Terraform inside the Jenkins Docker container so the pipeline can run `terraform` commands.

#### Created Terraform configuration files to provision an ec2 server
The config creates a VPC, subnet, internet gateway, route table, security group and a `t2.micro` instance with the latest Amazon Linux 2023 AMI and `entry-script.sh` as user data. SSH is allowed from my IP and the Jenkins server IP.

`variables.tf` and `main.tf`:

    root@PC:~/modules/terraform/java-terraform# cat variables.tf
    variable vpc_cidr_block {
        default = "10.0.0.0/16"
    }
    variable subnet_cidr_block {
        default = "10.0.10.0/24"
    }
    variable avail_zone {
        default = "eu-central-1a"
    }
    variable env_prefix {
        default = "dev"
    }
    variable my_ip{
        default = "<my-ip>/32"
    }
    variable jenkins_ip {
        default = "142.93.104.61/32"
    }
    variable instance_type{
        default = "t2.micro"
    }
    variable region {
        default = "eu-central-1"
    }

    root@PC:~/modules/terraform/java-terraform# cat main.tf
    provider "aws" {
        region = var.region
    }
    
    resource "aws_vpc" "myapp-vpc" {
        cidr_block = var.vpc_cidr_block
        tags = {
            Name: "${var.env_prefix}-vpc"
        }
    }
    
    resource "aws_subnet" "myapp-subnet-1" {
        vpc_id = aws_vpc.myapp-vpc.id
        cidr_block = var.subnet_cidr_block
        availability_zone = var.avail_zone
        tags = {
            Name: "${var.env_prefix}-subnet-1"
        }
    }
    
    resource "aws_internet_gateway" "myapp-igw" {
        vpc_id = aws_vpc.myapp-vpc.id
        tags = {
            Name: "${var.env_prefix}-igw"
        }
    }
    
    resource "aws_default_route_table" "main-rtb" {
        default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
    
        route{
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.myapp-igw.id
        }
        tags = {
            Name: "${var.env_prefix}-main-rtb"
        }
    }
    
    resource "aws_default_security_group" "default-sg" {
        vpc_id = aws_vpc.myapp-vpc.id
    
        ingress{
            from_port = 22
            to_port = 22
            protocol = "TCP"
            cidr_blocks = [var.my_ip, var.jenkins_ip]
        }
    
        ingress{
            from_port = 8080
            to_port = 8080
            protocol = "TCP"
            cidr_blocks = ["0.0.0.0/0"]
        }
    
        egress{
            from_port = 0
            to_port = 0
            protocol = "-1"
            cidr_blocks = ["0.0.0.0/0"]
            prefix_list_ids = []
        }
    
        tags = {
            Name: "${var.env_prefix}-default-sg"
        }
    }
    
    data "aws_ami" "latest-amazon-linux-image" {
        most_recent = true
        owners = ["amazon"]
        filter {
            name = "name"
            values = ["al2023-ami-2023.*-x86_64"]
        }
        filter{
            name = "virtualization-type"
            values = ["hvm"]
        }
    }
    
    resource "aws_instance" "myapp-server" {
        ami = data.aws_ami.latest-amazon-linux-image.id
        instance_type = var.instance_type
    
        subnet_id = aws_subnet.myapp-subnet-1.id
        vpc_security_group_ids = [aws_default_security_group.default-sg.id]
        availability_zone = var.avail_zone
    
        associate_public_ip_address = true
        key_name = "myapp-key-pair"
    
        user_data = file("entry-script.sh")
    
        user_data_replace_on_change = true
    
        tags = {
            Name: "${var.env_prefix}-server"
        }
    }
    
    output "ec2_public_ip" {
        value = aws_instance.myapp-server.public_ip
    }

#### Created entry-script.sh and server-cmds.sh
`entry-script.sh` installs Docker and Docker Compose when the server starts. `server-cmds.sh` runs on the server during deploy: it logs in to Docker Hub and starts the containers with Docker Compose.

`server-cmds.sh`:

    root@PC:~/modules/terraform/java-terraform# cat server-cmds.sh
    #!/usr/bin/env bash
    
    export IMAGE=$1
    export DOCKER_USER=$2
    export DOCKER_PWD=$3
    
    echo $DOCKER_PWD | docker login -u $DOCKER_USER --password-stdin
    docker-compose -f docker-compose.yaml up --detach
    echo "success"

#### Adjusted Jenkinsfile to include provision and deployment stages (with Docker Login)
The pipeline builds the jar, builds and pushes the image, runs Terraform in the `provision server` stage, and deploys over SSH. The EC2 IP comes from `terraform output -raw ec2_public_ip`, and the deploy stage waits 90 seconds for the server to finish starting up.

`Jenkinsfile`:

    root@PC:~/modules/terraform/java-terraform# cat Jenkinsfile
    #!/usr/bin/env groovy
    
    library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
        [$class: 'GitSCMSource',
         remote: 'https://github.com/emrearabacioglu/jenkins-shared-library.git',
         credentialsId: 'github-credentials'
        ]
    )
    pipeline {
        agent any
        
        tools {
            maven 'maven-3.9'
        }
        environment {
            IMAGE_NAME = "emrearabacioglu/demo-app:1.1.12-4"
        }
        stages {
            stage('build app') {
                steps {
                    script {
                        echo 'building application jar...'
                        buildJar()
                    }
                }
            }
            stage('build image') {
                steps {
                    script {
                        echo 'building the docker image...'
                        buildImage(env.IMAGE_NAME)
                        dockerLogin()
                        dockerPush(env.IMAGE_NAME)
                    }
                }
            } 
            stage("provision server" ) {
                environment {
                    AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                    AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_access_secret_key')
                    TF_VAR_env_prefix = 'test'
                }
              steps {
                script {
                    dir ('terraform') {
                        sh "terraform init"
                        sh "terraform apply --auto-approve"
                        env.EC2_PUBLIC_IP = sh (
                            script: "terraform output -raw ec2_public_ip",
                            returnStdout: true
                        ).trim()
                    }
                }
              }
            }
            stage('deploy') {
                environment {
                    DOCKER_CREDS = credentials('docker-hub-repo')
                }
                steps {
                    script {
                        echo"waiting initialization"
                        sleep(time: 90, unit: "SECONDS")
    
                        echo 'deploying docker image to EC2...'
                        echo "${EC2_PUBLIC_IP}"
    
                        def shellCmd = "bash ./server-cmds.sh ${IMAGE_NAME} ${DOCKER_CREDS_USR} ${DOCKER_CREDS_PSW}"
                        def ec2Instance = "ec2-user@${EC2_PUBLIC_IP}"
    
                        sshagent(['server-ssh-key']) {
                            sh "scp -o StrictHostKeyChecking=no server-cmds.sh ${ec2Instance}:/home/ec2-user"
                            sh "scp -o StrictHostKeyChecking=no docker-compose.yaml ${ec2Instance}:/home/ec2-user"
                            sh "ssh -o StrictHostKeyChecking=no ${ec2Instance} ${shellCmd}"
                        }
                    }
                }               
            }
        }
    }

#### Pipeline Run
All stages passed: jar built, image pushed to Docker Hub, Terraform had no changes to make (the server already existed), and the containers were started on EC2.

Pipeline log:

    Started by user emre
    ...
    [Pipeline] { (build app)
    ...
    [INFO] BUILD SUCCESS
    ...
    [Pipeline] { (build image)
    ...
    + docker build -t emrearabacioglu/demo-app:1.1.12-4 .
    ...
    + docker login -u emrearabacioglu --password-stdin
    Login Succeeded
    + docker push emrearabacioglu/demo-app:1.1.12-4
    ...
    1.1.12-4: digest: sha256:378325c256fab6f2f5b6613244c89d22e0ecd65eb7aef03ff738845e603964a5 size: 1159
    ...
    [Pipeline] { (provision server)
    ...
    + terraform apply --auto-approve
    No changes. Your infrastructure matches the configuration.
    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
    Outputs:
    ec2_public_ip = "3.75.191.235"
    ...
    [Pipeline] { (deploy)
    ...
    + scp -o StrictHostKeyChecking=no server-cmds.sh ec2-user@3.75.191.235:/home/ec2-user
    + scp -o StrictHostKeyChecking=no docker-compose.yaml ec2-user@3.75.191.235:/home/ec2-user
    + ssh -o StrictHostKeyChecking=no ec2-user@3.75.191.235 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.12-4 emrearabacioglu ****
    Login Succeeded
    ...
    Image emrearabacioglu/demo-app:1.1.12-4 Pulled
    Container ec2-user-postgres-1 Started
    success
    ...
    Finished: SUCCESS

<img width="1881" height="516" alt="image" src="https://github.com/user-attachments/assets/a91d42a1-bb18-4ccb-8892-5315caa8faf0" />

<img width="1907" height="931" alt="image" src="https://github.com/user-attachments/assets/21635cc0-bee7-489a-bcdb-891fdf1ec03b" />

#### Check on the Server
Connected to the instance and listed the running containers:

    root@PC:~/.ssh# ssh -i myapp-key-pair.pem ec2-user@3.75.191.235
    ...
    [ec2-user@ip-10-0-10-92 ~]$ docker ps
    CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                                       NAMES
    a008008b9c2b   postgres:16   "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   ec2-user-postgres-1
    f61c820ffc2e   nginx         "/docker-entrypoint.…"   9 minutes ago   Up 9 minutes   0.0.0.0:8080->80/tcp, :::8080->80/tcp       elated_chaplygin

</details>

******

<details>
<summary>Demo Project: Configure a Shared Remote State</summary>
 <br />

### Demo Executed: Store the Terraform state in S3

#### Infrastructure Teardown & Preparation
Before switching to remote state, destroyed the existing infrastructure manually from inside the Jenkins container, so the old local state would not conflict with the new backend.

#### AWS S3 Bucket Creation
Created an S3 bucket for the state file. This way Jenkins and my local machine use the same state.

#### Terraform Configuration Update
Added an `s3` backend to the `terraform` block in `main.tf`, so the state goes to the bucket instead of the Jenkins workspace:

    terraform {
      required_version = ">= 0.12"
      backend "s3" {
        bucket = "myapp-tf-s3-bucket-3673"
        key = "myapp/state.tfstate"
        region = "eu-central-1"
      }
    }

#### Executed CI/CD Pipeline with Remote Backend
Ran the pipeline again. `terraform init` configured the S3 backend, the apply created the server, and the app was deployed:

    Running in /var/jenkins_home/workspace/java-terraform_master/terraform
    ...
    + terraform init
    Initializing the backend...
    
    Successfully configured the backend "s3"! Terraform will automatically
    use this backend unless the backend configuration changes.
    
    Initializing provider plugins...
    - Reusing previous version of hashicorp/aws from the dependency lock file
    - Using previously-installed hashicorp/aws v6.63.0
    
    Terraform has been successfully initialized!
    ...
    + terraform apply --auto-approve
    data.aws_ami.latest-amazon-linux-image: Reading...
    data.aws_ami.latest-amazon-linux-image: Read complete after 0s [id=ami-030f85e68f5db92a9]
    ...
    aws_instance.myapp-server: Creating...
    aws_instance.myapp-server: Still creating... [00m10s elapsed]
    aws_instance.myapp-server: Creation complete after 12s [id=i-046a115228b08ed10]
    
    Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
    
    Outputs:
    ec2_public_ip = "3.64.13.241"
    ...
    + ssh -o StrictHostKeyChecking=no ec2-user@3.64.13.241 bash ./server-cmds.sh emrearabacioglu/demo-app:1.1.12-4 emrearabacioglu ****
    ...
    Login Succeeded
    Image emrearabacioglu/demo-app:1.1.12-4 Pulled 
    Image postgres:16 Pulled 
    Container ec2-user-postgres-1 Started
    success
    ...
    Finished: SUCCESS

#### Remote State Verification
Ran `terraform init` locally in the same folder. It connected to the same S3 backend, and `terraform state list` showed the resources Jenkins had created:

    root@PC:~/modules/terraform/java-terraform (master)# cd terraform/
    root@PC:~/modules/terraform/java-terraform/terraform (master)# terraform init
    Initializing the backend...
    
    Successfully configured the backend "s3"! Terraform will automatically
    use this backend unless the backend configuration changes.
    ...
    Terraform has been successfully initialized!
    
    root@PC:~/modules/terraform/java-terraform/terraform (master)# terraform state list
    data.aws_ami.latest-amazon-linux-image
    aws_default_route_table.main-rtb
    aws_default_security_group.default-sg
    aws_instance.myapp-server
    aws_internet_gateway.myapp-igw
    aws_subnet.myapp-subnet-1
    aws_vpc.myapp-vpc

<img width="1907" height="546" alt="image" src="https://github.com/user-attachments/assets/e5011bed-271e-4e43-9bb3-7e7aa5041282" />

</details>

******
