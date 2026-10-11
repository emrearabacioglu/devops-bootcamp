# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate configuring EC2 Server Instances

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
Tags before and after running the script:
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
