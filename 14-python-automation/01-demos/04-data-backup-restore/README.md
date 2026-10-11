# Data Backup & Restore

**Technologies:** Python, Boto3, AWS

Three Python scripts for EC2 volumes: one creates snapshots of the production volumes, one deletes old snapshots, and one restores a volume from the latest snapshot.

## Summary
- `terraform/main.tf` creates 2 EC2 instances in `eu-central-1a`, tagged `prod` and `dev`. `volume_tags` puts the same tags on their EBS volumes, so the scripts can filter the volumes by tag.
- `volume-backups.py` gets the volumes tagged `Name=prod` with `describe_volumes()` and creates a snapshot of each one with `create_snapshot()`. The `schedule` package runs it every 20 seconds (short interval only for the demo).
- `cleanup-snapshots.py` gets the snapshots of each `prod` volume (`OwnerIds=['self']` and a `volume-id` filter), sorts them by `StartTime` and deletes all except the 2 newest. My first version sorted all snapshots together without the loop over the volumes, so it also deleted the snapshots of the `dev` volume (see NOTES.md). The script in this folder loops over the `prod` volumes.
- `restore-volume.py` finds the volume of the `prod` instance (`i-0f98507bffe8e0a67`, set in the script), takes its latest snapshot and creates a new volume from it in `eu-central-1a`. It waits until the new volume is `available` and attaches it to the instance as `/dev/xvdb`.

## Run
```bash
pip install boto3 schedule
python volume-backups.py
python cleanup-snapshots.py
python restore-volume.py
```

## Result
The backup script creates a new snapshot of the `prod` volume on every run, and the restore script attaches the new volume once it is `available`:
```
(.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/04-automate-backup-restore/volume-backups.py
{'Tags': [], 'SnapshotId': 'snap-0ef771913ca01adb3', 'VolumeId': 'vol-00b821a5e6eb7006b', 'State': 'pending', 'StartTime': datetime.datetime(2026, 10, 6, 13, 2, 1, 97000, tzinfo=tzutc()), ..., 'VolumeSize': 8, 'Encrypted': False, 'ResponseMetadata': {...}}
{'Tags': [], 'SnapshotId': 'snap-073d147c6e34cac72', 'VolumeId': 'vol-00b821a5e6eb7006b', 'State': 'pending', 'StartTime': datetime.datetime(2026, 10, 6, 13, 2, 21, 714000, tzinfo=tzutc()), ..., 'VolumeSize': 8, 'Encrypted': False, 'ResponseMetadata': {...}}

(.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/04-automate-backup-restore/restore-volume.py
2026-10-06 13:02:21.714000+00:00
creating
creating
...
available
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
