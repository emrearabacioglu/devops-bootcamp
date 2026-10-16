# EXERCISE 1: Working with Subnets in AWS
# Get all the subnets in your default region
# Print the subnet Ids

import boto3 

client = boto3.client("ec2")
response = client.describe_subnets()
for subnet in response["Subnets"]:
    subnetid = subnet["SubnetId"]
    az = subnet["AvailabilityZone"]
    print(f"Subnet ID: {subnetid} Availability Zone: {az}")