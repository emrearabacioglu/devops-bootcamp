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
 
 ### Demo Executed: AWS Resource Tagging and Targeted Destruction


#### Added Tags to Existing Resources
Updated the `main.tf` configuration file to assign specific metadata tags (such as `Name` and `vpc_env`) to the existing Virtual Private Cloud (VPC) and subnets. Executed the deployment to apply these in-place modifications to the active AWS resources.

<img width="1688" height="555" alt="image" src="https://github.com/user-attachments/assets/5bc7d76e-5fdb-43b3-8c0b-3ca4e09ae949" />
<img width="1692" height="545" alt="image" src="https://github.com/user-attachments/assets/e09c9e8e-de96-4862-8633-bb9e1f431589" />



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
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 1s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-2: Refreshing state... [id=subnet-03b6a0bb1fff7080d]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place
    
    Terraform will perform the following actions:
    
      # aws_subnet.dev-subnet-1 will be updated in-place
      ~ resource "aws_subnet" "dev-subnet-1" {
            id                                             = "subnet-07584f50927802677"
          ~ tags                                           = {
              + "Name" = "subnet-1-dev"
            }
          ~ tags_all                                       = {
              + "Name" = "subnet-1-dev"
            }
            # (20 unchanged attributes hidden)
        }
    
      # aws_subnet.dev-subnet-2 will be updated in-place
      ~ resource "aws_subnet" "dev-subnet-2" {
            id                                             = "subnet-03b6a0bb1fff7080d"
          ~ tags                                           = {
              + "Name" = "subnet-2-dev"
            }
          ~ tags_all                                       = {
              + "Name" = "subnet-2-dev"
            }
            # (20 unchanged attributes hidden)
        }
    
      # aws_vpc.development-vpc will be updated in-place
      ~ resource "aws_vpc" "development-vpc" {
            id                                   = "vpc-0cd62b99a8d300dd6"
          ~ tags                                 = {
              + "Name"    = "developnet"
              + "vpc_env" = "dev"
            }
          ~ tags_all                             = {
              + "Name"    = "developnet"
              + "vpc_env" = "dev"
            }
            # (19 unchanged attributes hidden)
        }
    
    Plan: 0 to add, 3 to change, 0 to destroy.
    
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.
    
      Enter a value: yes
    
    aws_subnet.dev-subnet-2: Modifying... [id=subnet-03b6a0bb1fff7080d]
    aws_vpc.development-vpc: Modifying... [id=vpc-0cd62b99a8d300dd6]
    aws_subnet.dev-subnet-2: Modifications complete after 1s [id=subnet-03b6a0bb1fff7080d]
    aws_vpc.development-vpc: Modifications complete after 1s [id=vpc-0cd62b99a8d300dd6]
    aws_subnet.dev-subnet-1: Modifying... [id=subnet-07584f50927802677]
    aws_subnet.dev-subnet-1: Modifications complete after 1s [id=subnet-07584f50927802677]
    
    Apply complete! Resources: 0 added, 3 changed, 0 destroyed.

#### Removed Tag
Demonstrated configuration state alignment by removing the `vpc_env` tag from the `development-vpc` configuration. Applied the changes to accurately reflect the removal (marked as `-> null`) within the active AWS infrastructure.


    root@PC:~/modules/terraform# terraform apply
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 1s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-2: Refreshing state... [id=subnet-03b6a0bb1fff7080d]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place
    
    Terraform will perform the following actions:
    
      # aws_vpc.development-vpc will be updated in-place
      ~ resource "aws_vpc" "development-vpc" {
            id                                   = "vpc-0cd62b99a8d300dd6"
          ~ tags                                 = {
                "Name"    = "development"
              - "vpc_env" = "dev" -> null
            }
          ~ tags_all                             = {
              - "vpc_env" = "dev" -> null
                # (1 unchanged element hidden)
            }
            # (19 unchanged attributes hidden)
        }
    
    Plan: 0 to add, 1 to change, 0 to destroy.
    
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.
    
      Enter a value: yes
    
    aws_vpc.development-vpc: Modifying... [id=vpc-0cd62b99a8d300dd6]
    aws_vpc.development-vpc: Modifications complete after 1s [id=vpc-0cd62b99a8d300dd6]
    
    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.

#### Destroyed a Resource
Demonstrated precise infrastructure teardown by utilizing the targeted destroy command. Successfully decommissioned the specific `dev-subnet-2` resource without impacting or destroying the rest of the existing network architecture.

<img width="1912" height="483" alt="image" src="https://github.com/user-attachments/assets/ac62f14b-a414-4fda-90ce-4c1dc158852e" />


    root@PC:~/modules/terraform# terraform destroy -target aws_subnet.dev-subnet-2
    data.aws_vpc.existing_vpc: Reading...
    data.aws_vpc.existing_vpc: Read complete after 0s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-2: Refreshing state... [id=subnet-03b6a0bb1fff7080d]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      - destroy
    
    Terraform will perform the following actions:
    
      # aws_subnet.dev-subnet-2 will be destroyed
      - resource "aws_subnet" "dev-subnet-2" {
          - arn                                            = "arn:aws:ec2:eu-central-1:731872836472:subnet/subnet-03b6a0bb1fff7080d" -> null
          - assign_ipv6_address_on_creation                = false -> null
          - availability_zone                              = "eu-central-1a" -> null
          - availability_zone_id                           = "euc1-az2" -> null
          - cidr_block                                     = "172.31.48.0/20" -> null
          - enable_dns64                                   = false -> null
          - enable_lni_at_device_index                     = 0 -> null
          - enable_resource_name_dns_a_record_on_launch    = false -> null
          - enable_resource_name_dns_aaaa_record_on_launch = false -> null
          - id                                             = "subnet-03b6a0bb1fff7080d" -> null
          - ipv6_native                                    = false -> null
          - map_customer_owned_ip_on_launch                = false -> null
          - map_public_ip_on_launch                        = false -> null
          - owner_id                                       = "731872836472" -> null
          - private_dns_hostname_type_on_launch            = "ip-name" -> null
          - region                                         = "eu-central-1" -> null
          - tags                                           = {
              - "Name" = "subnet-2-default"
            } -> null
          - tags_all                                       = {
              - "Name" = "subnet-2-default"
            } -> null
          - vpc_id                                         = "vpc-0511d66bb75f2d673" -> null
            # (4 unchanged attributes hidden)
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
    
    Do you really want to destroy all resources?
      Terraform will destroy all your managed infrastructure, as shown above.
      There is no undo. Only 'yes' will be accepted to confirm.
    
      Enter a value: yes
    
    aws_subnet.dev-subnet-2: Destroying... [id=subnet-03b6a0bb1fff7080d]
    aws_subnet.dev-subnet-2: Destruction complete after 0s
    
    Destroy complete! Resources: 1 destroyed.


 
</details>

******

<details>
<summary>More Terraform commands</summary>
 <br />
 
### Demo Executed: Infrastructure Lifecycle Management


#### Executed Preview Command
Generated a speculative execution plan to review pending infrastructure modifications prior to actual deployment. The output detailed the exact resources slated for creation, enabling safe validation of the configuration code against the current state file.

    root@PC:~/modules/terraform# terraform plan
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 0s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
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
          + tags                                           = {
              + "Name" = "subnet-2-default"
            }
          + tags_all                                       = {
              + "Name" = "subnet-2-default"
            }
          + vpc_id                                         = "vpc-0511d66bb75f2d673"
        }
    
    Plan: 1 to add, 0 to change, 0 to destroy.
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    
    Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.

#### Applied Config File Without Preview
Streamlined the deployment pipeline by executing the configuration application with the auto-approve flag. This bypassed the interactive manual confirmation prompt, instantly provisioning the targeted subnet (`dev-subnet-2`) into the AWS environment.


    root@PC:~/modules/terraform# terraform apply -auto-approve
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 0s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
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
          + tags                                           = {
              + "Name" = "subnet-2-default"
            }
          + tags_all                                       = {
              + "Name" = "subnet-2-default"
            }
          + vpc_id                                         = "vpc-0511d66bb75f2d673"
        }
    
    Plan: 1 to add, 0 to change, 0 to destroy.
    aws_subnet.dev-subnet-2: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-006d83142a1928369]
    
    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

#### Destroyed Complete Infrastructure
Executed a comprehensive environment teardown. Initiated the global destroy command, validated the execution plan marking all managed resources (two subnets and one VPC) for deletion, and authorized the full decommissioning of the simulated network architecture.


    root@PC:~/modules/terraform# terraform destroy
    data.aws_vpc.existing_vpc: Reading...
    aws_vpc.development-vpc: Refreshing state... [id=vpc-0cd62b99a8d300dd6]
    data.aws_vpc.existing_vpc: Read complete after 0s [id=vpc-0511d66bb75f2d673]
    aws_subnet.dev-subnet-2: Refreshing state... [id=subnet-006d83142a1928369]
    aws_subnet.dev-subnet-1: Refreshing state... [id=subnet-07584f50927802677]
    
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with
    the following symbols:
      - destroy
    
    Terraform will perform the following actions:
    
      # aws_subnet.dev-subnet-1 will be destroyed
      - resource "aws_subnet" "dev-subnet-1" {
          - arn                                            = "arn:aws:ec2:eu-central-1:731872836472:subnet/subnet-07584f50927802677" -> null
          - assign_ipv6_address_on_creation                = false -> null
          - availability_zone                              = "eu-central-1a" -> null
          - availability_zone_id                           = "euc1-az2" -> null
          - cidr_block                                     = "10.0.10.0/24" -> null
          - enable_dns64                                   = false -> null
          - enable_lni_at_device_index                     = 0 -> null
          - enable_resource_name_dns_a_record_on_launch    = false -> null
          - enable_resource_name_dns_aaaa_record_on_launch = false -> null
          - id                                             = "subnet-07584f50927802677" -> null
          - ipv6_native                                    = false -> null
          - map_customer_owned_ip_on_launch                = false -> null
          - map_public_ip_on_launch                        = false -> null
          - owner_id                                       = "731872836472" -> null
          - private_dns_hostname_type_on_launch            = "ip-name" -> null
          - region                                         = "eu-central-1" -> null
          - tags                                           = {
              - "Name" = "subnet-1-dev"
            } -> null
          - tags_all                                       = {
              - "Name" = "subnet-1-dev"
            } -> null
          - vpc_id                                         = "vpc-0cd62b99a8d300dd6" -> null
            # (4 unchanged attributes hidden)
        }
    
      # aws_subnet.dev-subnet-2 will be destroyed
      - resource "aws_subnet" "dev-subnet-2" {
          - arn                                            = "arn:aws:ec2:eu-central-1:731872836472:subnet/subnet-006d83142a1928369" -> null
          - assign_ipv6_address_on_creation                = false -> null
          - availability_zone                              = "eu-central-1a" -> null
          - availability_zone_id                           = "euc1-az2" -> null
          - cidr_block                                     = "172.31.48.0/20" -> null
          - enable_dns64                                   = false -> null
          - enable_lni_at_device_index                     = 0 -> null
          - enable_resource_name_dns_a_record_on_launch    = false -> null
          - enable_resource_name_dns_aaaa_record_on_launch = false -> null
          - id                                             = "subnet-006d83142a1928369" -> null
          - ipv6_native                                    = false -> null
          - map_customer_owned_ip_on_launch                = false -> null
          - map_public_ip_on_launch                        = false -> null
          - owner_id                                       = "731872836472" -> null
          - private_dns_hostname_type_on_launch            = "ip-name" -> null
          - region                                         = "eu-central-1" -> null
          - tags                                           = {
              - "Name" = "subnet-2-default"
            } -> null
          - tags_all                                       = {
              - "Name" = "subnet-2-default"
            } -> null
          - vpc_id                                         = "vpc-0511d66bb75f2d673" -> null
            # (4 unchanged attributes hidden)
        }
    
      # aws_vpc.development-vpc will be destroyed
      - resource "aws_vpc" "development-vpc" {
          - arn                                  = "arn:aws:ec2:eu-central-1:731872836472:vpc/vpc-0cd62b99a8d300dd6" -> null
          - assign_generated_ipv6_cidr_block     = false -> null
          - cidr_block                           = "10.0.0.0/16" -> null
          - default_network_acl_id               = "acl-000003a010b920691" -> null
          - default_route_table_id               = "rtb-03c87f77f2b741028" -> null
          - default_security_group_id            = "sg-08a828fed82461591" -> null
          - dhcp_options_id                      = "dopt-0edc4ad56ac7a15fc" -> null
          - enable_dns_hostnames                 = false -> null
          - enable_dns_support                   = true -> null
          - enable_network_address_usage_metrics = false -> null
          - id                                   = "vpc-0cd62b99a8d300dd6" -> null
          - instance_tenancy                     = "default" -> null
          - ipv6_netmask_length                  = 0 -> null
          - main_route_table_id                  = "rtb-03c87f77f2b741028" -> null
          - owner_id                             = "731872836472" -> null
          - region                               = "eu-central-1" -> null
          - tags                                 = {
              - "Name" = "development"
            } -> null
          - tags_all                             = {
              - "Name" = "development"
            } -> null
            # (4 unchanged attributes hidden)
        }
    
    Plan: 0 to add, 0 to change, 3 to destroy.
    
    Do you really want to destroy all resources?
      Terraform will destroy all your managed infrastructure, as shown above.
      There is no undo. Only 'yes' will be accepted to confirm.
    
      Enter a value: yes
    
    aws_subnet.dev-subnet-2: Destroying... [id=subnet-006d83142a1928369]
    aws_subnet.dev-subnet-1: Destroying... [id=subnet-07584f50927802677]
    aws_subnet.dev-subnet-1: Destruction complete after 0s
    aws_vpc.development-vpc: Destroying... [id=vpc-0cd62b99a8d300dd6]
    aws_subnet.dev-subnet-2: Destruction complete after 1s
    aws_vpc.development-vpc: Destruction complete after 1s
    
    Destroy complete! Resources: 3 destroyed.

 
</details>

******

<details>
<summary>Terraform State</summary>
 <br />
 
 ### Demo Executed: Automated Provisioning and State Management

#### Applied Config File Without Preview
Demonstrated non-interactive infrastructure deployment by executing an automated apply command. Successfully provisioned a custom Virtual Private Cloud (VPC) alongside two distinct subnets (one in the custom VPC, one in the default VPC) without requiring manual execution prompts.

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
    data.aws_vpc.existing_vpc: Reading...
    data.aws_vpc.existing_vpc: Read complete after 1s [id=vpc-0511d66bb75f2d673]
    
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
          + tags                                           = {
              + "Name" = "subnet-1-dev"
            }
          + tags_all                                       = {
              + "Name" = "subnet-1-dev"
            }
          + vpc_id                                         = (known after apply)
        }
    
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
          + tags                                           = {
              + "Name" = "subnet-2-default"
            }
          + tags_all                                       = {
              + "Name" = "subnet-2-default"
            }
          + vpc_id                                         = "vpc-0511d66bb75f2d673"
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
          + tags                                 = {
              + "Name" = "development"
            }
          + tags_all                             = {
              + "Name" = "development"
            }
        }
    
    Plan: 3 to add, 0 to change, 0 to destroy.
    aws_subnet.dev-subnet-2: Creating...
    aws_vpc.development-vpc: Creating...
    aws_subnet.dev-subnet-2: Creation complete after 1s [id=subnet-0f84f579e64b837ff]
    aws_vpc.development-vpc: Creation complete after 1s [id=vpc-047ff10c7a5f9ab73]
    aws_subnet.dev-subnet-1: Creating...
    aws_subnet.dev-subnet-1: Creation complete after 1s [id=subnet-0bd0a41afd6671e9d]
    
    Apply complete! Resources: 3 added, 0 changed, 0 destroyed.

#### Inspected Terraform State
Utilized the built-in Terraform state management utilities to audit the active environment. Extracted a high-level inventory of all managed entities and executed targeted queries to expose the underlying attributes, Amazon Resource Names (ARNs), and assigned tags for a specific deployed subnet instance.

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
        customer_owned_ipv4_pool                       = null
        enable_dns64                                   = false
        enable_lni_at_device_index                     = 0
        enable_resource_name_dns_a_record_on_launch    = false
        enable_resource_name_dns_aaaa_record_on_launch = false
        id                                             = "subnet-0bd0a41afd6671e9d"
        ipv6_cidr_block                                = null
        ipv6_cidr_block_association_id                 = null
        ipv6_native                                    = false
        map_customer_owned_ip_on_launch                = false
        map_public_ip_on_launch                        = false
        outpost_arn                                    = null
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
 
 ### Demo Executed: Defining and Retrieving Terraform Output Values


#### Defined Output Values in Configuration
Authored the `main.tf` configuration file to provision a Virtual Private Cloud (VPC) and a Subnet. Appended specific `output` blocks to the configuration to explicitly extract and expose the dynamically generated AWS resource IDs (`dev-vpc-id` and `dev-subnet-id`) to the console upon deployment.

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
Executed an automated deployment of the declared infrastructure. Validated that Terraform successfully created the AWS resources and parsed the output variables, printing the exact AWS assigned resource IDs (`vpc-0e7925ca7de335498` and `subnet-0ee36142d5bbbb3de`) directly to the terminal output for immediate reference.
```bash
    root@PC:~/modules/terraform# terraform apply --auto-approve
    
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
          + tags                                           = {
              + "Name" = "subnet-1-dev"
            }
          + tags_all                                       = {
              + "Name" = "subnet-1-dev"
            }
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
          + tags                                 = {
              + "Name" = "development"
            }
          + tags_all                             = {
              + "Name" = "development"
            }
        }
    
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
 
 ### Demo Executed: Terraform Variable Management and Credential Security


#### Restricted Value of Variable by Defining a Type
Refactored the infrastructure code to utilize variables instead of hardcoded values. Enforced strict data structures by defining variable types (e.g., `list(string)` and `list(object)`). Validated this restriction by intentionally passing an incompatible data type, triggering Terraform's type constraint validation, before correcting it to an object array.
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
Resolved the type constraint error by restructuring the variables into a complex `list(object)` structure. Demonstrated variable injection by passing a dedicated environment-specific configuration file (`terraform-dev.tfvars`) via the CLI flag, ensuring clean and reusable code.
```bash
    root@PC:~/modules/terraform# cat main.tf
    # ... [Provider block hidden] ...
    
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
    # ... [Subnet resource utilizing var.cidr_blocks[1] hidden] ...
    
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
To adhere to security best practices, hardcoded AWS Access Keys and Secret Keys were stripped from the `main.tf` provider block. Authenticated the deployment dynamically by extracting temporary credentials directly from the host's secure environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`). 
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
Demonstrated a third method of variable injection by utilizing Terraform's native `TF_VAR_` environment variable prefix. Dynamically controlled the AWS Availability Zone targeting by updating the system environment, successfully forcing a state replacement (from `eu-central-1a` to `eu-central-1b`) without altering any configuration files.
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
 Committer: root <root@PC.localdomain>
Your name and email address were configured automatically based
on your username and hostname. Please check that they are accurate.
You can suppress this message by setting them explicitly:

    git config --global user.name "Your Name"
    git config --global user.email you@example.com

After doing this, you may fix the identity used for this commit with:

    git commit --amend --reset-author

 4 files changed, 97 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 .terraform.lock.hcl
 create mode 100644 main.tf
 create mode 100644 providers.tf
root@PC:~/modules/terraform# git push -u origin master
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Delta compression using up to 8 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 2.19 KiB | 2.19 MiB/s, done.
Total 6 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/emrearabacioglu/terraform.git
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.

```
 
</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 1</summary>
 <br />
 
 ### Demo Executed: AWS VPC Networking and Security Configuration



#### Created VPC & Subnet
Defined and provisioned a custom Virtual Private Cloud (VPC) alongside a Subnet using dynamically injected variables for CIDR blocks and environment prefixes. The deployment automatically cleared outdated infrastructure and established the new targeted networking foundation.

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
Provisioned an Internet Gateway (IGW) and attached it to the VPC. Subsequently, authored a custom Route Table configuring a default route (`0.0.0.0/0`) directed to the IGW to enable external internet connectivity.
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
Explicitly bound the created subnet to the custom Route Table utilizing the `aws_route_table_association` resource, ensuring external traffic correctly routes through the defined Internet Gateway.

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
Refactored the network routing strategy by deprecating the custom Route Table and explicit association in favor of managing the implicitly generated Default Route Table. Utilized the `aws_default_route_table` resource to assign the Internet Gateway directly to the main VPC route table.
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
Authored a custom Security Group to strictly control network traffic flow. Established inbound (ingress) rules for SSH (Port 22) restricted to a specific IP address and HTTP (Port 8080) open to the internet, while allowing all outbound (egress) traffic.
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
Pivoted the security architecture from a custom group to managing the VPC's natively generated Default Security Group. Deployed the `aws_default_security_group` resource, applying identical ingress and egress rulesets while maintaining a cleaner AWS resource inventory.

<img width="1708" height="701" alt="image" src="https://github.com/user-attachments/assets/5e46d969-e203-46c8-a0b3-878d8277420d" />

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

 
</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 2</summary>
 <br />
 
 ### Demo Executed: Automated EC2 Provisioning and SSH Key Management


#### Created EC2 Instance (Manual Key Pair Approach)
Demonstrated the deployment of an EC2 instance (`t2.micro`) utilizing an Amazon Machine Image (AMI). Initially, the workflow relied on a manually generated SSH key pair (`server-key-pair.pem`) downloaded directly from the AWS Console. 

To ensure SSH client compatibility and enforce security best practices, the permissions on the downloaded private key were strictly locked down using standard Linux file permission protocols.
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
Validated the infrastructure configuration and network connectivity by successfully establishing a secure shell (SSH) session into the newly provisioned Amazon Linux 2023 server using the manually downloaded `.pem` key.
```bash
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/server-key-pair.pem ec2-user@18.192.8.225
    The authenticity of host '18.192.8.225 (18.192.8.225)' can't be established.
    ED25519 key fingerprint is SHA256:4jQZsvFbwQg80vSiK0YNniKkZj3t/In4CCjv2qZr1AI.
    This key is not known by any other names.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    Warning: Permanently added '18.192.8.225' (ED25519) to the list of known hosts.
       ,     #_
       ~\_  ####_        Amazon Linux 2023
    ...
    [ec2-user@ip-10-0-10-185 ~]$ exit
    logout
    Connection to 18.192.8.225 closed.
```
#### Configured SSH Key Pair in Terraform Config File
Refactored the infrastructure code to fully automate the SSH key lifecycle, eliminating the need for manual AWS Console interactions. Integrated the `aws_key_pair` resource into the Terraform configuration, pointing it to a pre-existing local public key (`id_rsa.pub`).

```bash
    root@PC:~/modules/terraform (feature/EC2)# cat main.tf
    # ... [Networking and Security Group configurations hidden] ...
    
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
Applied the updated configuration. Terraform detected the change in the `key_name` attribute and enforced an infrastructure replacement (destroy and re-create). The new EC2 instance was successfully provisioned and bound to the automatically generated, Terraform-managed SSH key pair.
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
Successfully accessed the newly recreated server using the locally generated default RSA key. Verified that the automated key injection worked flawlessly by executing an SSH connection without explicitly passing the `-i` flag (as the SSH agent automatically utilizes default keys like `id_rsa`). Afterward, the legacy, manually downloaded `.pem` key was securely removed from the local filesystem.
```bash
    root@PC:~/modules/terraform (feature/EC2)# terraform state show aws_instance.myapp-server
    # ... [State output confirming public IP: 35.157.195.225] ...
    
    root@PC:~/modules/terraform (feature/EC2)# ssh -i ~/.ssh/id_rsa ec2-user@35.157.195.225
    ...
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# ssh ec2-user@35.157.195.225
    ...
    Last login: Sat Sep  5 18:22:33 2026 from 195.174.91.91
    [ec2-user@ip-10-0-10-105 ~]$ exit
    logout
    Connection to 35.157.195.225 closed.
    
    root@PC:~/modules/terraform (feature/EC2)# rm ~/.ssh/server-key-pair.pem
```
 <img width="1905" height="927" alt="image" src="https://github.com/user-attachments/assets/0db12caa-d5f5-477e-aaec-b77d1ef9698c" />
<img width="1909" height="404" alt="image" src="https://github.com/user-attachments/assets/70dd2aec-28e6-4274-a35b-bfe648b36bd6" />

</details>

******

<details>
<summary>Demo Project 1: Automate your AWS Infrastructure - Part 3</summary>
 <br />
 
 ### Demo Executed: Automated EC2 Provisioning with Docker & Nginx

#### Configured Terraform to install Docker and run nginx image
Automated the server bootstrapping process by injecting a `user_data` script into the EC2 instance configuration. This script was designed to update the OS, install Docker, append the `ec2-user` to the Docker group, and deploy an Nginx container automatically upon boot. Validated the deployment by connecting via SSH, confirming the necessity of a session refresh to inherit the newly assigned group permissions, and ultimately verifying the running container.
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
Refactored the infrastructure codebase by extracting the inline `user_data` script into a dedicated external shell script (`entry-script.sh`). Utilized Terraform's `file()` function to parse the script, improving modularity and code readability. Deployed the updated configuration and successfully validated the container status on the newly provisioned instance.
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
Confirmed the successful deployment and correct Security Group network configurations by accessing the Nginx default landing page via a web browser using the dynamically provisioned EC2 instance's public IP address.

<img width="1344" height="315" alt="image" src="https://github.com/user-attachments/assets/348edfb5-4007-419a-9f96-7bf693536620" />



 
</details>

******

<details>
<summary>Provisioners</summary>
 <br />
 
 ### Demo Executed: Automating Operations with Terraform Provisioners


#### Used “remote-exec” provisioner
Demonstrated the execution of inline commands directly on a newly provisioned EC2 instance using the `remote-exec` provisioner. Since Terraform provisioners only run during resource creation, the `-replace` flag was utilized to force the destruction and recreation of the existing instance. The connection was successfully established via SSH within Terraform, and the inline command successfully created a new directory (`newdir`) on the remote server, which was subsequently verified via a manual SSH session.
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
Configured the `file` provisioner to securely copy assets from the local host machine to the newly created remote EC2 instance. This eliminates the need for manual secure copy (SCP) commands. The configuration specified copying the local `entry-script.sh` directly into the remote `ec2-user` home directory.
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
Configured the `local-exec` provisioner to trigger a local script execution on the host machine running Terraform immediately after the resource creation. This was utilized to extract the dynamically generated EC2 public IP address and pipe it directly into a local text file (`output.txt`) for immediate reference or downstream automation usage. 

Additionally, the `remote-exec` script functionality was configured alongside it to run the file previously uploaded by the `file` provisioner.
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
<summary>Modules</summary>
 <br />
 
 ### Demo Executed: Modularizing Terraform Configurations

#### Extracted output values, variables and providers into its own file
Restructured the monolithic `main.tf` by separating core configuration elements into distinct files to improve maintainability and adherence to Terraform best practices. Outputs were moved to `outputs.tf`, variables to `variables.tf`, and provider requirements were isolated into `providers.tf`.
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
Extracted the subnet, internet gateway, and route table definitions into a dedicated child module located in `modules/subnet`. Refactored the root `main.tf` to invoke this module, passing the necessary network variables and referencing the dynamically generated subnet ID through module outputs.
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
Further decoupled the infrastructure by migrating the security group, AMI data fetch, SSH key pair, and EC2 instance deployment logic into a `modules/webserver` directory. The root configuration was updated to call this module, injecting variables and establishing dependencies (e.g., retrieving the `subnet_id` generated by the `myapp-subnet` module). During this phase, addressed syntax errors related to missing equals signs in block definitions and relative pathing for the `user_data` script.
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
#### Executed terraform apply successfully
Reinitialized the Terraform backend to register the newly created modules. Deployed the modularized infrastructure, which effectively destroyed the legacy root-level resources and successfully re-provisioned them under the new module hierarchy. Validated the deployment via an SSH connection, confirming the automated installation of Docker.
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
