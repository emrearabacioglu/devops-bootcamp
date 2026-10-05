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
<summary>Health Check: EC2 Status Checks</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Write a Scheduled Task in Python</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Configure Server: Add Environment Tags to EC2 Instances</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>EKS cluster information</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Backup EC2 Volumes: Automate creating Snapshots</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Automate cleanup of old Snapshots</summary>
 <br />

 content will be here

 
</details>

******

<details>
<summary>Automate restoring EC2 Volume from the Backup</summary>
 <br />

 content will be here

 
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
