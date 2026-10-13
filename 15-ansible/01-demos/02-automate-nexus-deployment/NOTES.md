# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate Nexus Deployment

### Demo Executed: Deploy Nexus - Install Java and Unpack the Nexus Installer

#### Preparation
Created a new Ubuntu droplet on DigitalOcean (`206.189.51.31`) for Nexus and added it to the inventory of the project. The playbook automates the manual Nexus installation steps.

#### Playbook
* **Install java and net-tools** – Nexus 3.70.1 and later needs Java 17, so `openjdk-17-jre-headless` is installed instead of Java 8. `net-tools` provides `netstat` to check the Nexus port later.
* **Download/Unpack Nexus Installer**:
    * `get_url` downloads the latest Nexus to `/opt/`. The result is saved with `register`, so the next task can use the downloaded file path (`download_result.dest`).
    * `unarchive` with `remote_src: yes` unpacks the file that is already on the server (by default it copies the file from my machine).
    * The unpacked folder name contains the Nexus version, which changes with every release. `find` gets the folder name, so it is not hardcoded.
    * The folder is renamed to `/opt/nexus` with `mv`. `stat` checks if `/opt/nexus` already exists and `when` skips the task in that case, so the `shell` task doesn't fail on the next run.

`deploy-nexus.yaml`:

```yaml
    ---
    - name: Install java and net-tools
      hosts: 206.189.51.31
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600

        - name: Install Java 17
          apt: name=openjdk-17-jre-headless

        - name: Install net-tools
          apt: name=net-tools

    - name: Download/Unpack Nexus Installer
      hosts: 206.189.51.31
      tasks:
        - name: Download Nexus
          get_url:
            url: https://download.sonatype.com/nexus/3/latest-linux-x86_64.tar.gz
            dest: /opt/
          register: download_result

        - name: Untar Nexus Installer
          unarchive:
            src: "{{download_result.dest}}"
            dest: /opt/
            remote_src: yes

        - name: Find nexus folder
          find:
            paths: /opt/
            pattern: "nexus-*"
            file_type: directory
          register: find_result

        - name: Check if nexus folder stats
          stat:
            path: /opt/nexus
          register: stat_result

        - name: Rename nexus folder
          shell: mv {{find_result.files[0].path}} /opt/nexus
          when: not stat_result.stat.exists
```

#### Execution
The folder was already renamed in an earlier run, so the rename task is skipped:

```bash
    (.venv) root@PC:~/modules/ansible/02-nexus# ansible-playbook -i hosts deploy-nexus.yaml
    ...
    PLAY [Download/Unpack Nexus Installer] ****
    ...
    TASK [Download Nexus] ****
    ok: [206.189.51.31]

    TASK [Untar Nexus Installer] ****
    changed: [206.189.51.31]

    TASK [Find nexus folder] ****
    ok: [206.189.51.31]

    TASK [Check if nexus folder stats] ****
    ok: [206.189.51.31]

    TASK [Rename nexus folder] ****
    skipping: [206.189.51.31]

    PLAY RECAP ****
    206.189.51.31              : ok=9    changed=1    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

### Demo Executed: Deploy Nexus - Nexus User, Start and Verify

#### Changes in the Existing Plays
* The servers are now targeted with the inventory group `nexus_server` instead of the IP address.
* The inventory file is defined in the project's `ansible.cfg`, so the playbook runs without `-i hosts`.
* The `stat` check moved to the beginning of the play. The archive is unpacked only if `/opt/nexus` doesn't exist, so a second run doesn't create a new `nexus-3.x` folder.

#### New Plays
* **Create nexus user and group** – the `group` and `user` modules create the `nexus` user. The `file` module with `recurse: yes` gives the ownership of the `nexus` and `sonatype-work` folders to this user.
* **Start nexus with nexus user** – the play runs as `nexus` (`become_user`). In the Nexus version I installed (3.96) there is no `nexus.rc` file anymore, the `run_as_user` setting is in the `bin/nexus` script. `lineinfile` replaces the line `run_as_user=''` with `run_as_user="nexus"`, so Nexus also switches to the `nexus` user when it is started as root.
* **Verify nexus running** – checks the process with `ps`. Nexus needs a few minutes to start, so `wait_for` waits until port `8081` is open (max. 5 minutes) instead of a fixed pause. Then `netstat` shows the open port.

Full playbook:

```yaml
    ---
    - name: Install java and net-tools
      hosts: nexus_server
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600

        - name: Install Java 17
          apt: name=openjdk-17-jre-headless

        - name: Install net-tools
          apt: name=net-tools

    - name: Download/Unpack Nexus Installer
      hosts: nexus_server
      tasks:
        - name: Check nexus folder stats
          stat:
            path: /opt/nexus
          register: stat_result

        - name: Download Nexus
          get_url:
            url: https://download.sonatype.com/nexus/3/latest-linux-x86_64.tar.gz
            dest: /opt/
          register: download_result

        - name: Untar Nexus Installer
          unarchive:
            src: "{{download_result.dest}}"
            dest: /opt/
            remote_src: yes
          when: not stat_result.stat.exists

        - name: Find nexus folder
          find:
            paths: /opt/
            pattern: "nexus-*"
            file_type: directory
          register: find_result

        - name: Rename nexus folder
          shell: mv {{find_result.files[0].path}} /opt/nexus
          when: not stat_result.stat.exists

    - name: Create nexus user and group
      hosts: nexus_server
      tasks:
        - name: Create nexus group
          group:
            name: nexus
            state: present

        - name: Create nexus user
          user:
            name: nexus
            group: nexus

        - name: Match user and group of nexus folder
          file:
            path: /opt/nexus
            state: directory
            owner: nexus
            group: nexus
            recurse: yes

        - name: Match user and group of sonatype folder
          file:
            path: /opt/sonatype-work
            state: directory
            owner: nexus
            group: nexus
            recurse: yes

    - name: Start nexus with nexus user
      hosts: nexus_server
      become: True
      become_user: nexus
      tasks:
        - name: Set run_as_user nexus
          lineinfile:
            path: /opt/nexus/bin/nexus
            regexp: '^run_as_user='
            line: run_as_user="nexus"

        - name: Run nexus
          command: /opt/nexus/bin/nexus start

    - name: Verify nexus running
      hosts: nexus_server
      tasks:
        - name: Check with ps
          shell: ps aux | grep nexus
          register: app_status
        - debug: msg={{app_status.stdout_lines}}

        - name: Wait for nexus port
          wait_for:
            port: 8081
            timeout: 300

        - name: Check with netstat
          shell: netstat -lnpt
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
Nexus runs as the `nexus` user and listens on port `8081`:

```bash
    (.venv) root@PC:~/modules/ansible/02-nexus# ansible-playbook deploy-nexus.yaml
    ...
    PLAY [Start nexus with nexus user] ****
    ...
    TASK [Set run_as_user nexus] ****
    ok: [165.22.31.85]

    TASK [Run nexus] ****
    changed: [165.22.31.85]

    PLAY [Verify nexus running] ****
    ...
    TASK [debug] ****
    ok: [165.22.31.85] => {
        "msg": [
            "nexus       2025  104 31.3 6802596 2548640 ?     Sl   16:36   6:29 /opt/nexus/jdk/temurin_21.0.11_10_linux_x86_64/jdk-21.0.11+10/bin/java -server ... -jar /opt/nexus/bin/sonatype-nexus-repository-3.96.4-01.jar",
            ...
        ]
    }

    TASK [Wait for nexus port] ****
    ok: [165.22.31.85]

    TASK [Check with netstat] ****
    changed: [165.22.31.85]

    TASK [debug] ****
    ok: [165.22.31.85] => {
        "msg": [
            "Active Internet connections (only servers)",
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    ",
            "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1/init              ",
            "tcp6       0      0 :::8081                 :::*                    LISTEN      2025/java           ",
            ...
        ]
    }

    PLAY RECAP ****
    165.22.31.85               : ok=22   changed=3    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```
