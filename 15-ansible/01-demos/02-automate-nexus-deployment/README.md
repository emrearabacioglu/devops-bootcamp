# Automate Nexus Deployment

**Technologies:** Ansible, Nexus, DigitalOcean, Java, Linux

I wrote an Ansible playbook that installs Nexus on a DigitalOcean droplet, runs it with its own `nexus` Linux user and checks that it is running.

## Summary
1. Created an Ubuntu droplet on DigitalOcean and added it to the `hosts` file in the group `nexus_server`. `ansible.cfg` sets `inventory = hosts`, so the playbook runs without `-i`.
2. `deploy-nexus.yaml` automates the manual Nexus install steps, play by play:
   - **Install java and net-tools**: installs `openjdk-17-jre-headless` (Nexus 3.70.1 and later needs Java 17) and `net-tools` for `netstat`.
   - **Download/Unpack Nexus Installer**: `get_url` downloads the latest Nexus to `/opt/`, `unarchive` with `remote_src: yes` unpacks it on the server, `find` gets the versioned `nexus-*` folder and `shell` renames it to `/opt/nexus`. A `stat` check skips the unpack and the rename when `/opt/nexus` already exists, so a second run doesn't fail.
   - **Create nexus user and group**: creates the `nexus` user and group and gives it ownership of `/opt/nexus` and `/opt/sonatype-work` (`file` with `recurse: yes`).
   - **Start nexus with nexus user**: in Nexus 3.96 there is no `nexus.rc` anymore, so `lineinfile` sets `run_as_user="nexus"` in `/opt/nexus/bin/nexus`. Then `nexus start` runs as the `nexus` user.
   - **Verify nexus running**: `ps aux | grep nexus`, then `wait_for` waits until port `8081` is open (max. 5 minutes) and `netstat -lnpt` shows the port.

## Run
```bash
ansible-playbook deploy-nexus.yaml
```

## Result
Nexus runs as the `nexus` user and listens on port `8081`:
```
TASK [debug] ****
ok: [165.22.31.85] => {
    "msg": [
        "nexus       2025  104 31.3 6802596 2548640 ?     Sl   16:36   6:29 /opt/nexus/jdk/temurin_21.0.11_10_linux_x86_64/jdk-21.0.11+10/bin/java -server ... -jar /opt/nexus/bin/sonatype-nexus-repository-3.96.4-01.jar",
...
TASK [Wait for nexus port] ****
ok: [165.22.31.85]
...
        "tcp6       0      0 :::8081                 :::*                    LISTEN      2025/java           ",
...
PLAY RECAP ****
165.22.31.85               : ok=22   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
