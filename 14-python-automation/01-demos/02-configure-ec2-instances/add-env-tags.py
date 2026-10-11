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