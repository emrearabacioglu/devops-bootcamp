******

<details>
<summary>Getting familiar with Boto</summary>
 <br />

### Demo Executed: Creating and Listing VPCs with Boto3

#### VPC and Subnet Creation
Used both Boto3 interfaces: the `resource` interface to create a VPC with two subnets and a `Name` tag, and the low-level `client` interface to list all VPCs in the region with their CIDR block state. AWS credentials and region are read from the local AWS CLI configuration (`~/.aws`).

```python
    import boto3

    ec2_client = boto3.client('ec2')
    ec2_resource = boto3.resource('ec2')


    new_vpc = ec2_resource.create_vpc(
        CidrBlock="10.0.0.0/16"
    )

    new_vpc.create_subnet(
        CidrBlock="10.0.1.0/24"
    )

    new_vpc.create_subnet(
        CidrBlock="10.0.2.0/24"
    )

    new_vpc.create_tags(
        Tags=[
            {
                'Key': 'Name',
                'Value': 'auto-vpc'
            },
        ]
    )

    all_available_vpcs = ec2_client.describe_vpcs()
    vpcs = all_available_vpcs["Vpcs"]

    for vpc in vpcs :
        print(vpc["VpcId"])
        cidr_block_assoc_sets = vpc["CidrBlockAssociationSet"]
        for assoc_set in cidr_block_assoc_sets:
            print(assoc_set["CidrBlockState"])
```

#### Execution
Raw `describe_vpcs()` response (only the default VPC exists at this point):
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/main.py
    {'Vpcs': [{'OwnerId': '731872836472', 'InstanceTenancy': 'default', 'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-08bedd3101e78434d', 'CidrBlock': '172.31.0.0/16', 'CidrBlockState': {'State': 'associated'}}], 'IsDefault': True, ..., 'VpcId': 'vpc-0511d66bb75f2d673', 'State': 'available', 'CidrBlock': '172.31.0.0/16', ...}], 'ResponseMetadata': {..., 'HTTPStatusCode': 200, ...}}
```

Parsed output with only the VPC ID and CIDR block state:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/main.py
    vpc-0511d66bb75f2d673
    {'State': 'associated'}
```

After running the full script: the new `auto-vpc` is listed next to the default VPC:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/main.py
    vpc-0724dc1839ebd1745
    {'State': 'associated'}
    vpc-0511d66bb75f2d673
    {'State': 'associated'}
```
<img width="1709" height="554" alt="image" src="https://github.com/user-attachments/assets/d3a66f24-14aa-47bc-993d-1e81f0d753bd" />

</details>

******

<details>
<summary>Health Check: EC2 Status Checks & Scheduled Task</summary>
 <br />

### Demo Executed: EC2 Status Checks with Boto3 and a Scheduled Task

#### Preparation: 3 EC2 Instances with Terraform
Reused the AWS infrastructure from the Terraform module (VPC, subnet, security group, internet gateway, route table, key pair) and created 3 EC2 instances to monitor.

```hcl
    provider "aws" {
        region = "eu-central-1"
    }

    variable vpc_cidr_block {}
    variable subnet_cidr_block {}
    variable avail_zone {}
    variable env_prefix {}
    variable instance_type {}
    variable my_ip {}
    variable public_key_location {}

    data "aws_ami" "amazon-linux-image" {
      most_recent = true
      owners      = ["amazon"]

      filter {
        name   = "name"
        values = ["al2023-ami-2023.*-x86_64"]
      }

      filter {
        name   = "virtualization-type"
        values = ["hvm"]
      }
    }

    output "ami_id" {
      value = data.aws_ami.amazon-linux-image.id
    }

    resource "aws_vpc" "myapp-vpc" {
      cidr_block = var.vpc_cidr_block
      tags = {
        Name = "${var.env_prefix}-vpc"
      }
    }

    resource "aws_subnet" "myapp-subnet-1" {
      vpc_id            = aws_vpc.myapp-vpc.id
      cidr_block        = var.subnet_cidr_block
      availability_zone = var.avail_zone
      tags = {
        Name = "${var.env_prefix}-subnet-1"
      }
    }

    resource "aws_security_group" "myapp-sg" {
      name   = "myapp-sg"
      vpc_id = aws_vpc.myapp-vpc.id

      ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = [var.my_ip]
      }

      ingress {
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }

      egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
        prefix_list_ids = []
      }

      tags = {
        Name = "${var.env_prefix}-sg"
      }
    }

    resource "aws_internet_gateway" "myapp-igw" {
      vpc_id = aws_vpc.myapp-vpc.id

      tags = {
        Name = "${var.env_prefix}-internet-gateway"
      }
    }

    resource "aws_route_table" "myapp-route-table" {
      vpc_id = aws_vpc.myapp-vpc.id

      route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.myapp-igw.id
      }

      # default route, mapping VPC CIDR block to "local", created implicitly and cannot be specified.

      tags = {
        Name = "${var.env_prefix}-route-table"
      }
    }

    # Associate subnet with Route Table
    resource "aws_route_table_association" "a-rtb-subnet" {
      subnet_id      = aws_subnet.myapp-subnet-1.id
      route_table_id = aws_route_table.myapp-route-table.id
    }

    resource "aws_key_pair" "ssh-key" {
      key_name   = "myapp-key"
      public_key = file(var.public_key_location)
    }

    output "server-ip" {
      value = aws_instance.myapp-server.public_ip
    }

    resource "aws_instance" "myapp-server" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }

    resource "aws_instance" "myapp-server-two" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server-two"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }

    resource "aws_instance" "myapp-server-three" {
      ami                         = data.aws_ami.amazon-linux-image.id
      instance_type               = var.instance_type
      key_name                    = aws_key_pair.ssh-key.key_name
      associate_public_ip_address = true
      subnet_id                   = aws_subnet.myapp-subnet-1.id
      vpc_security_group_ids      = [aws_security_group.myapp-sg.id]
      availability_zone           = var.avail_zone

      tags = {
        Name = "${var.env_prefix}-server-three"
      }

      user_data = file("entry-script.sh")

      user_data_replace_on_change = true
    }
```

Provisioned the instances:
```bash
    root@PC:~/modules/python-automation/01-ec2-health-check/terraform# terraform apply
    ...
    aws_instance.myapp-server-two: Refreshing state... [id=i-0957da2371a8ba1fc]
    aws_instance.myapp-server: Refreshing state... [id=i-0d9ab4ceff4be7078]
    ...
      # aws_instance.myapp-server-three will be created
      + resource "aws_instance" "myapp-server-three" {
          + ami                                  = "ami-0149e5f1dd5234430"
          + instance_type                        = "t3.micro"
          + tags                                 = {
              + "Name" = "dev-server-three"
            }
          ...
        }

    Plan: 1 to add, 0 to change, 0 to destroy.
    ...
    aws_instance.myapp-server-three: Creating...
    aws_instance.myapp-server-three: Creation complete after 15s [id=i-05ec8658146509a8d]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

#### Health Check Script with a Scheduler
`describe_instance_status()` returns the state (running, stopped, terminated…) and the two AWS status checks of each instance:

* **Instance status** – checks the instance itself (OS, network config)
* **System status** – checks the AWS hardware the instance runs on

`IncludeAllInstances=True` also returns instances that are not running; without it only running instances are listed. The `schedule` package runs the check every 5 seconds.

```python
    import boto3
    import schedule

    ec2_client = boto3.client('ec2', region_name="eu-central-1")
    ec2_resource = boto3.resource('ec2', region_name="eu-central-1")


    def check_instance_status():
        statuses = ec2_client.describe_instance_status(
            IncludeAllInstances=True
        )
        for status in statuses['InstanceStatuses']:
            ins_status = status['InstanceStatus']['Status']
            sys_status = status['SystemStatus']['Status']
            state = status['InstanceState']['Name']
            print(f"Instance {status['InstanceId']} is {state}. Instance status: {ins_status}, System status: {sys_status}")
        print("\n")

    schedule.every(5).seconds.do(check_instance_status)

    while True:
        schedule.run_pending()
```

#### Execution
All 3 instances running and healthy (`i-02155…` is an instance replaced earlier by Terraform, it is still listed as `terminated` because of `IncludeAllInstances=True`):
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/01-ec2-health-check/healthcheck.py
    Instance i-0957da2371a8ba1fc is running. Instance status: ok, System status: ok
    Instance i-05ec8658146509a8d is running. Instance status: ok, System status: ok
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
```

While the script was running, removed 2 instances with Terraform:
```bash
    root@PC:~/modules/python-automation/01-ec2-health-check/terraform# terraform apply --auto-approve
    ...
      # aws_instance.myapp-server-three will be destroyed
      # (because aws_instance.myapp-server-three is not in configuration)
    ...
      # aws_instance.myapp-server-two will be destroyed
      # (because aws_instance.myapp-server-two is not in configuration)
    ...
    Plan: 0 to add, 0 to change, 2 to destroy.
    aws_instance.myapp-server-three: Destroying... [id=i-05ec8658146509a8d]
    aws_instance.myapp-server-two: Destroying... [id=i-0957da2371a8ba1fc]
    aws_instance.myapp-server-three: Destruction complete after 31s
    aws_instance.myapp-server-two: Destruction complete after 31s

    Apply complete! Resources: 0 added, 0 changed, 2 destroyed.
```

The scheduled script picked up the state change on its next runs (`running` → `shutting-down` → `terminated`):
```bash
    Instance i-0957da2371a8ba1fc is running. Instance status: ok, System status: ok
    Instance i-05ec8658146509a8d is running. Instance status: ok, System status: ok
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable


    Instance i-0957da2371a8ba1fc is shutting-down. Instance status: not-applicable, System status: not-applicable
    Instance i-05ec8658146509a8d is shutting-down. Instance status: not-applicable, System status: not-applicable
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
    ...

    Instance i-0957da2371a8ba1fc is terminated. Instance status: not-applicable, System status: not-applicable
    Instance i-05ec8658146509a8d is terminated. Instance status: not-applicable, System status: not-applicable
    Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
    Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
```

</details>

******

<details>
<summary>Configure Server: Add Environment Tags to EC2 Instances</summary>
 <br />

 ### Demo Executed: Adding Environment Tags to EC2 Instances in Multiple Regions

#### Preparation
Created 3 EC2 instances with Terraform in the default VPCs of two regions: 2 in Frankfurt (`eu-central-1`) and 1 in Paris (`eu-west-3`).

#### Tagging Script
The script uses a separate Boto3 client and resource per region. It collects the IDs of all instances in each region with `describe_instances()` and adds an `environment` tag with `create_tags()`:

* Frankfurt instances → `environment=prod`
* Paris instances → `environment=dev`

A small helper function prints the instance tags before and after tagging (only non-terminated instances, filtered on the AWS side).

```python
    import boto3

    ec2_client_frankfurt = boto3.client('ec2', region_name="eu-central-1")
    ec2_resource_frankfurt = boto3.resource('ec2', region_name="eu-central-1")

    ec2_client_paris = boto3.client('ec2', region_name="eu-west-3")
    ec2_resource_paris = boto3.resource('ec2', region_name="eu-west-3")

    def print_tags(client, region):
        instances = client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}]
        )
        for res in instances['Reservations']:
            for ins in res['Instances']:
                tags = ", ".join(f"{t['Key']}={t['Value']}" for t in ins.get('Tags', []))
                print(f"{region:<10} {ins['InstanceId']}  {ins['State']['Name']:<8}  {tags}")

    print("----- BEFORE -----")
    print_tags(ec2_client_frankfurt, "frankfurt")
    print_tags(ec2_client_paris, "paris")

    instances_ids_frankfurt = []
    instances_ids_paris = []

    reservations_frankfurt = ec2_client_frankfurt.describe_instances()['Reservations']
    for res in reservations_frankfurt:
        instances = res['Instances']
        for ins in instances:
            instances_ids_frankfurt.append(ins['InstanceId'])

    response = ec2_resource_frankfurt.create_tags(
        Resources=instances_ids_frankfurt,
        Tags=[
            {
                'Key': 'environment',
                'Value': 'prod'
            },
        ]
    )

    reservations_paris = ec2_client_paris.describe_instances()['Reservations']
    for res in reservations_paris:
        instances = res['Instances']
        for ins in instances:
            instances_ids_paris.append(ins['InstanceId'])

    response = ec2_resource_paris.create_tags(
        Resources=instances_ids_paris,
        Tags=[
            {
                'Key': 'environment',
                'Value': 'dev'
            },
        ]
    )

    print("----- AFTER -----")
    print_tags(ec2_client_frankfurt, "frankfurt")
    print_tags(ec2_client_paris, "paris")
```

#### Execution
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/02-auto-configure-ec2/terraform/add-env-tags.py
    ----- BEFORE -----
    frankfurt  i-092f937388bb7e4d5  running   Name=frankfurt-server-2
    frankfurt  i-0b665156e2e5c8b72  running   Name=frankfurt-server-1
    paris      i-021c02f8b628d8340  running   Name=paris-server-1
    ----- AFTER -----
    frankfurt  i-092f937388bb7e4d5  running   Name=frankfurt-server-2, environment=prod
    frankfurt  i-0b665156e2e5c8b72  running   Name=frankfurt-server-1, environment=prod
    paris      i-021c02f8b628d8340  running   environment=dev, Name=paris-server-1
```

 
</details>

******

<details>
<summary>EKS cluster information</summary>
 <br />

### Demo Executed: Displaying EKS Cluster Information with Boto3

#### Preparation: EKS Cluster with Terraform
Created an EKS cluster with the official Terraform registry modules: the VPC module (same setup as in the Terraform module) and the EKS module with a managed node group of 3 `t2.small` nodes.

```hcl
    module "eks" {
      source  = "terraform-aws-modules/eks/aws"
      version = "21.25.0"

      name               = "myapp-eks-cluster"
      kubernetes_version = "1.33"

      subnet_ids = module.myapp-vpc.private_subnets
      vpc_id     = module.myapp-vpc.vpc_id

      endpoint_public_access                   = true
      enable_cluster_creator_admin_permissions = true

      addons = {
        coredns                = {}
        eks-pod-identity-agent = {
          before_compute = true
        }
        kube-proxy             = {}
        vpc-cni                = {
          before_compute = true
        }
      }

      eks_managed_node_groups = {
        dev = {
          ami_type       = "AL2023_x86_64_STANDARD"
          instance_types = ["t2.small"]

          min_size     = 1
          max_size     = 3
          desired_size = 3
        }
      }

      tags = {
        environment = "development"
        application = "myapp"
      }
    }
```

```bash
    root@PC:~/modules/python-automation/03-automate-display-eks/terraform# terraform apply
    ...
    Plan: 62 to add, 0 to change, 0 to destroy.
    ...
    module.eks.aws_eks_cluster.this[0]: Creation complete after 10m22s [id=myapp-eks-cluster]
    ...
    module.eks.module.eks_managed_node_group["dev"].aws_eks_node_group.this[0]: Creation complete after 1m50s [id=myapp-eks-cluster:dev-bcd8951e7992956431dc8f3880]
    ...
    Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
```

#### Cluster Information Script
The script lists all EKS clusters in the region with `list_clusters()` and gets the details of each cluster with `describe_cluster()`: status, API endpoint and Kubernetes version.

```python
    import boto3

    client = boto3.client('eks', region_name="eu-central-1")
    clusters = client.list_clusters()['clusters']

    for cluster in clusters:
        response = client.describe_cluster(
            name=cluster
        )
        cluster_info = response['cluster']
        cluster_status = cluster_info['status']
        cluster_endpoint = cluster_info['endpoint']
        cluster_version = cluster_info['version']
        print(f"Cluster {cluster} status is {cluster_status}\nCluster endpoint:{cluster_endpoint}\nCluster version: {cluster_version}")
```

#### Execution
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/03-automate-display-eks/eks-check.py
    Cluster myapp-eks-cluster status is ACTIVE
    Cluster endpoint:https://E6719366FF375E2340E8C825A540B76C.gr7.eu-central-1.eks.amazonaws.com
    Cluster version: 1.33
```

 
</details>

******

<details>
<summary>Backup EC2 Volumes: Automate creating Snapshots</summary>
 <br />

### Demo Executed: Scheduled Snapshots of Production EC2 Volumes

#### Preparation
Created 2 EC2 instances with Terraform in Frankfurt (`eu-central-1a`), tagged as `prod` and `dev`. The same tags were also added to their EBS volumes (`volume_tags`), so the volumes can be filtered by tag.

#### Backup Script
The script gets the volumes with `describe_volumes()`, filtered by the tag `Name=prod`, and creates a snapshot of each volume with `create_snapshot()`. The `schedule` package runs the backup every 20 seconds (short interval only for the demo).

```python
    import boto3
    import schedule

    ec2_client = boto3.client('ec2', region_name="eu-central-1")

    def create_volume_snapshots():
        volumes = ec2_client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['prod']
                }
            ]
        )
        for volume in volumes['Volumes']:
            new_snapshot = ec2_client.create_snapshot(
                VolumeId=volume['VolumeId']
            )
            print(new_snapshot)

    schedule.every(20).seconds.do(create_volume_snapshots)

    while True:
        schedule.run_pending()
```

#### Execution
Only the volume of the `prod` server (`vol-00b821a5e6eb7006b`) is backed up, a new snapshot is created on every run:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/04-automate-backup-restore/volume-backups.py
    {'Tags': [], 'SnapshotId': 'snap-0ef771913ca01adb3', 'VolumeId': 'vol-00b821a5e6eb7006b', 'State': 'pending', 'StartTime': datetime.datetime(2026, 10, 6, 13, 2, 1, 97000, tzinfo=tzutc()), ..., 'VolumeSize': 8, 'Encrypted': False, 'ResponseMetadata': {...}}
    {'Tags': [], 'SnapshotId': 'snap-073d147c6e34cac72', 'VolumeId': 'vol-00b821a5e6eb7006b', 'State': 'pending', 'StartTime': datetime.datetime(2026, 10, 6, 13, 2, 21, 714000, tzinfo=tzutc()), ..., 'VolumeSize': 8, 'Encrypted': False, 'ResponseMetadata': {...}}
```


 
</details>

******

<details>
<summary>Automate cleanup of old Snapshots</summary>
 <br />

### Demo Executed: Keep Only the Latest 2 Snapshots per Volume

#### Preparation
Used the same `prod` and `dev` EC2 instances and the snapshots created in the backup demo. Before the cleanup there were 6 snapshots: 4 of the `prod` volume and 2 of the `dev` volume.

#### Cleanup Script
The script gets the `prod` volumes with `describe_volumes()` and, for each volume, its snapshots with `describe_snapshots()`. `OwnerIds=['self']` returns only my own snapshots (not public AWS snapshots), and the `volume-id` filter limits the list to that volume. The snapshots are sorted by `StartTime` (newest first) with `itemgetter`, and everything except the first 2 is deleted with `delete_snapshot()`.

```python
    import boto3
    from operator import itemgetter

    ec2_client = boto3.client('ec2', region_name="eu-central-1")

    volumes = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['prod']
            }
        ]
    )

    for volume in volumes['Volumes']:
        snapshots= ec2_client.describe_snapshots(
            OwnerIds=['self'],
            Filters=[
                    {
                        'Name': 'volume-id',
                        'Values': [volume['VolumeId']]
                    }
                ]
        )

        sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)

        for snap in sorted_by_date[2:]:
            response = ec2_client.delete_snapshot(
                SnapshotId=snap['SnapshotId']
            )
            print(response)
```

#### Execution
The first version sorted all snapshots together, without the volume loop. It kept the latest 2 snapshots overall (both from `prod`) and deleted the other 4, so the `dev` volume lost all its backups:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/04-automate-backup-restore/cleanup-snapshots.py
    {'ResponseMetadata': {..., 'HTTPStatusCode': 200, ...}}
    {'ResponseMetadata': {..., 'HTTPStatusCode': 200, ...}}
    {'ResponseMetadata': {..., 'HTTPStatusCode': 200, ...}}
    {'ResponseMetadata': {..., 'HTTPStatusCode': 200, ...}}
```

| Volume | Snapshot | StartTime | Result |
|---|---|---|---|
| prod | `snap-073d147c6e34cac72` | 13:02:21 | kept |
| prod | `snap-0ef771913ca01adb3` | 13:02:01 | kept |
| prod | `snap-031a7e1a0d2c90669` | 12:54:28 | deleted |
| dev | `snap-0fb9e6c4bf211daec` | 12:54:28 | deleted |
| prod | `snap-08e4ebcc0f6e3458e` | 12:50:13 | deleted |
| dev | `snap-08dea95a0175d86eb` | 12:50:13 | deleted |

 
</details>

******

<details>
<summary>Automate restoring EC2 Volume from the Backup</summary>
 <br />

### Demo Executed: Restore an EC2 Volume from the Latest Snapshot

#### Preparation
Used the same `prod` and `dev` EC2 instances and the snapshots left after the cleanup demo. The restore was done for the `prod` server (`i-0f98507bffe8e0a67`).

#### Restore Script
* Gets the volume attached to the instance with `describe_volumes()` and the `attachment.instance-id` filter.
* Gets the snapshots of that volume and picks the latest one (sorted by `StartTime`).
* Creates a new volume from the snapshot with `create_volume()` in the same AZ as the instance (`eu-central-1a`) and tags it as `prod`.
* A new volume can only be attached when it is `available`. The script checks the state in a loop and attaches the volume to the instance as `/dev/xvdb` with the boto3 resource (`Instance.attach_volume()`).

```python
    import boto3
    from operator import itemgetter

    ec2_client = boto3.client('ec2', region_name="eu-central-1")
    ec2_resource = boto3.resource('ec2', region_name="eu-central-1")

    instance_id = "i-0f98507bffe8e0a67"

    volumes = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'attachment.instance-id',
                'Values': [instance_id]
            }
        ]
    )

    instance_volume = volumes['Volumes'][0]

    snapshots = ec2_client.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [instance_volume['VolumeId']]
            }
        ]
    )

    latest_snapshot = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]
    print(latest_snapshot['StartTime'])

    new_volume = ec2_client.create_volume(
        SnapshotId=latest_snapshot['SnapshotId'],
        AvailabilityZone="eu-central-1a",
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'prod'
                    }
                ]
            }
        ]
    )

    while True:
        vol = ec2_resource.Volume(new_volume['VolumeId'])
        print(vol.state)
        if vol.state == 'available':
            ec2_resource.Instance(instance_id).attach_volume(
                VolumeId=new_volume['VolumeId'],
                Device='/dev/xvdb'
            )
            break
```

#### Execution
The latest snapshot of the `prod` volume was used. The new volume stayed in `creating` state for a few seconds, then it was attached to the instance as soon as it became `available`:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/04-automate-backup-restore/restore-volume.py
    2026-10-06 13:02:21.714000+00:00
    creating
    creating
    creating
    creating
    creating
    creating
    available
```
#### UI View:

<img width="1907" height="910" alt="image" src="https://github.com/user-attachments/assets/d7bd7481-8ed8-40d1-aa74-1ffd20d88505" />


 
</details>

******

<details>
<summary>Handling Errors</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Website Monitoring 1: Scheduled Task to Monitor Application Health</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Website Monitoring 2: Automated Email Notification</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Website Monitoring 3: Restart Application and Reboot Server</summary>
 <br />

 content will be here

 
</details>

******
