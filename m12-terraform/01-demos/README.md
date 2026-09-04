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
