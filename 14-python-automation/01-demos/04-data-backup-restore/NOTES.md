# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Data Backup & Restore

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

#### UI View
AWS console after the restore:

<img width="1907" height="910" alt="image" src="https://github.com/user-attachments/assets/d7bd7481-8ed8-40d1-aa74-1ffd20d88505" />
