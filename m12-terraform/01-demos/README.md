******

<details>
<summary>Local Setup & Providers</summary>
 <br />
 
 ### Demo Executed: Terraform Infrastructure and AWS Provider Initialization


#### Terraform Environment Installation
Provisioned the local Linux environment by securely importing the official HashiCorp GPG keys, adding the apt repository, and installing the Terraform CLI to enable Infrastructure as Code (IaC) deployments.

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

#### Use AWS Provider (Configuration)
Authored the foundational Terraform configuration files (`main.tf` and `providers.tf`). Defined the required AWS provider, pinned the target version, and established programmatic authentication credentials for the `eu-central-1` region.



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
Executed the Terraform initialization process to configure the backend, generate the dependency lock file (`.terraform.lock.hcl`), and successfully download the specified provider plugins (AWS and Linode).

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
 
 ### Demo Executed: AWS Network Provisioning with Terraform

#### Created new VPC and Subnet in that new VPC
Authored the declarative infrastructure configuration in `main.tf` to establish a custom Virtual Private Cloud (VPC) with a `10.0.0.0/16` CIDR block and an associated subnet within the `eu-central-1a` availability zone. Successfully deployed the configuration to provision the networking resources directly in the AWS environment.

<img width="1708" height="829" alt="image" src="https://github.com/user-attachments/assets/fee6e5c5-6a75-431e-87df-98412cdfeabb" />
<img width="1704" height="823" alt="image" src="https://github.com/user-attachments/assets/172a34b8-f721-4c8e-8db6-170fcc327b72" />


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
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with
    the following symbols:
      + create
    
    Terraform will perform the following actions:
    
      # aws_subnet.dev-subnet-1 will be created
      + resource "aws_subnet" "dev-subnet-1" {
          + arn                                            = (known after apply)
          + assign_ipv6_address_on_creation                = false
          + availability_zone                              = "eu-central-1a"
          + availability_zone_id                           = (known after apply)
          + cidr_block                                     = "10.0.10.0/24"
          + enable_dns64                                   = false
          + enable_resource_name_dns_a_record_on_launch    = false
          + enable_resource_name_dns_aaaa_record_on_launch = false
          + id                                             = (known after apply)
          + ipv6_cidr_block                                = (known after apply)
          + ipv6_cidr_block_association_id                 = (known after apply)
          + ipv6_native                                    = false
          + map_public_ip_on_launch                        = false
          + owner_id                                       = (known after apply)
          + private_dns_hostname_type_on_launch            = (known after apply)
          + region                                         = "eu-central-1"
          + tags_all                                       = (known after apply)
          + vpc_id                                         = (known after apply)
        }
    
      # aws_vpc.development-vpc will be created
      + resource "aws_vpc" "development-vpc" {
          + arn                                  = (known after apply)
          + cidr_block                           = "10.0.0.0/16"
          + default_network_acl_id               = (known after apply)
          + default_route_table_id               = (known after apply)
          + default_security_group_id            = (known after apply)
          + dhcp_options_id                      = (known after apply)
          + enable_dns_hostnames                 = (known after apply)
          + enable_dns_support                   = true
          + enable_network_address_usage_metrics = (known after apply)
          + id                                   = (known after apply)
          + instance_tenancy                     = "default"
          + ipv6_association_id                  = (known after apply)
          + ipv6_cidr_block                      = (known after apply)
          + ipv6_cidr_block_network_border_group = (known after apply)
          + main_route_table_id                  = (known after apply)
          + owner_id                             = (known after apply)
          + region                               = "eu-central-1"
          + tags_all                             = (known after apply)
        }
    
    Plan: 2 to add, 0 to change, 0 to destroy.
    
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.
    
      Enter a value: yes
    
    aws_vpc.development-vpc: Creating...
    aws_vpc.development-vpc: Creation complete after 2s [id=vpc-0cd62b99a8d300dd6]
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 0s [id=subnet-07584f50927802677]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```
#### Created new Subnet in existing default VPC (with data)
Expanded the Terraform configuration to implement a `data` block, enabling the dynamic retrieval of the existing AWS default VPC. Provisioned a secondary subnet (`172.31.48.0/20`) attached directly to the fetched default VPC ID. Validated infrastructure idempotency by re-executing the deployment, confirming the state precisely matched the codebase with zero required changes.

<img width="1696" height="825" alt="image" src="https://github.com/user-attachments/assets/ace68462-cfc6-4a00-bb6b-51cc0c88d257" />

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
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with
    the following symbols:
      + create
    
    Terraform will perform the following actions:
    
      # aws_subnet.dev-subnet-2 will be created
      + resource "aws_subnet" "dev-subnet-2" {
          + arn                                            = (known after apply)
          + assign_ipv6_address_on_creation                = false
          + availability_zone                              = "eu-central-1a"
          + availability_zone_id                           = (known after apply)
          + cidr_block                                     = "172.31.48.0/20"
          + enable_dns64                                   = false
          + enable_resource_name_dns_a_record_on_launch    = false
          + enable_resource_name_dns_aaaa_record_on_launch = false
          + id                                             = (known after apply)
          + ipv6_cidr_block                                = (known after apply)
          + ipv6_cidr_block_association_id                 = (known after apply)
          + ipv6_native                                    = false
          + map_public_ip_on_launch                        = false
          + owner_id                                       = (known after apply)
          + private_dns_hostname_type_on_launch            = (known after apply)
          + region                                         = "eu-central-1"
          + tags_all                                       = (known after apply)
          + vpc_id                                         = "vpc-0511d66bb75f2d673"
        }
    
    Plan: 1 to add, 0 to change, 0 to destroy.
    
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.
    
      Enter a value: yes
    
    aws_subnet.dev-subnet-2: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-03b6a0bb1fff7080d]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    
    root@PC:~/modules/terraform# terraform apply
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 0s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-2: Refreshing state... [id=subnet-03b6a0bb1fff7080d]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    No changes. Your infrastructure matches the configuration.
    
    Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
    
    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

```
 
</details>

******

<details>
<summary>Change/Destroy Resources</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>More Terraform commands</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Terraform State</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Terraform Output</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Variables</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Environment Variables</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Initialize Git Repository</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 3</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Provisioners</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Modules - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Modules - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Modules - Part 3</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 2: Terraform & AWS EKS - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 2: Terraform & AWS EKS - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 2: Terraform & AWS EKS - Part 3</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 3: Complete CI/CD with Terraform - Part 1</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 3: Complete CI/CD with Terraform - Part 2</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Demo Project 3: Complete CI/CD with Terraform - Part 3</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Terraform Remote State</summary>
 <br />
 
 **content will be here**
 
</details>

******

<details>
<summary>Terraform Best Practices</summary>
 <br />
 
 **content will be here**
 
</details>

******
