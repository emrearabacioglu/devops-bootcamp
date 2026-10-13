# Automate configuring EC2 Server Instances

**Technologies:** Python, Boto3, AWS

A Python script that adds an `environment` tag to all EC2 instances in two AWS regions.

## Summary
- `terraform/main.tf` creates 3 test instances in the default VPCs of two regions: `frankfurt-server-1` and `frankfurt-server-2` in `eu-central-1`, and `paris-server-1` in `eu-west-3` (second AWS provider with alias `paris`).
- `add-env-tags.py` uses a separate Boto3 client and resource for each region. It collects the instance IDs with `describe_instances()` and adds the tag with `create_tags()`:
  - Frankfurt → `environment=prod`
  - Paris → `environment=dev`
- The helper function `print_tags()` prints the tags of the non-terminated instances before and after tagging.

## Run
```bash
pip install boto3
python add-env-tags.py
```

## Result
Tags before and after the script, the `environment` tag is added in both regions:
```
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

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
