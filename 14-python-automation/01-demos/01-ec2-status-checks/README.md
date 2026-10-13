# Health Check: EC2 Status Checks

**Technologies:** Python, Boto3, AWS, Terraform

I created 3 EC2 instances with Terraform and wrote a Python script that prints the state and status checks of all EC2 instances every 5 seconds.

## Summary
- `terraform/main.tf` creates a VPC, subnet, internet gateway, route table, security group, key pair and 3 EC2 instances (Amazon Linux 2023) in `eu-central-1`. `terraform/entry-script.sh` installs Docker on each instance and starts an nginx container on port 8080.
- The variables are in `terraform/terraform.tfvars.example` (my IP is masked as `***`).
- `healthcheck.py` calls `describe_instance_status()` with Boto3 and prints the state, instance status and system status of every instance. `IncludeAllInstances=True` also lists instances that are not running.
- The `schedule` package runs the check every 5 seconds.
- While the script was running, I removed 2 instances from the Terraform config and ran `terraform apply --auto-approve`. The script showed them going from `running` to `shutting-down` to `terminated`.

## Run
```bash
cd terraform
terraform init
terraform apply
cd ..
pip install boto3 schedule
python healthcheck.py
```

## Result
All instances `ok`, then 2 of them shutting down and terminated after the Terraform change (`i-02155...` is an older instance that was already terminated):
```
Instance i-0957da2371a8ba1fc is running. Instance status: ok, System status: ok
Instance i-05ec8658146509a8d is running. Instance status: ok, System status: ok
Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
Instance i-02155a8d271ea4ba5 is terminated. Instance status: not-applicable, System status: not-applicable
...
Instance i-0957da2371a8ba1fc is shutting-down. Instance status: not-applicable, System status: not-applicable
Instance i-05ec8658146509a8d is shutting-down. Instance status: not-applicable, System status: not-applicable
Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
...
Instance i-0957da2371a8ba1fc is terminated. Instance status: not-applicable, System status: not-applicable
Instance i-05ec8658146509a8d is terminated. Instance status: not-applicable, System status: not-applicable
Instance i-0d9ab4ceff4be7078 is running. Instance status: ok, System status: ok
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
