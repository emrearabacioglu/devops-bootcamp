******

<details>
<summary>Local Setup & Providers</summary>
 <br />
 
 ### Demo Executed: Terraform Infrastructure and AWS Provider Initialization

*[Note: Since some infrastructure management tasks and credential generations are performed via web dashboards rather than the terminal, I highly recommend enriching this repository with relevant UI screenshots to visually demonstrate those configurations.]*

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
 
 **content will be here**
 
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
