# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automate Node.js application Deployment

### Demo Executed: Deploy Node.js Application - Install Node.js and Unpack the App

#### Preparation
* Created a new Ubuntu droplet on DigitalOcean (`188.166.34.20`) and added it to the inventory of the project.
* Took the Node.js application from the bootcamp repository and packaged it with `npm pack` into `nodejs-app-1.0.0.tgz`.

#### Playbook
The playbook has two plays:

* **Install node and npm** – updates the apt cache (skipped if it was updated in the last hour) and installs `nodejs` and `npm` with the `apt` module.
* **Deploy nodejs app** – the `unarchive` module copies the artifact from my machine to the server and unpacks it in `/root/`. The `src` path is relative to the playbook.

`deploy-node.yaml`:

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /root/
```

#### Execution
Ran the playbook:

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml

    PLAY [Install node and npm] ****

    TASK [Gathering Facts] ****
    ok: [188.166.34.20]

    TASK [Update apt repo and cache] ****
    ok: [188.166.34.20]

    TASK [Install nodejs and npm] ****
    ok: [188.166.34.20]

    PLAY [Deploy nodejs app] ****

    TASK [Gathering Facts] ****
    ok: [188.166.34.20]

    TASK [Unpack the nodejs file] ****
    changed: [188.166.34.20]

    PLAY RECAP ****
    188.166.34.20              : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

#### Verification on the Server
`npm pack` puts the application into a `package` folder, so the app is unpacked to `/root/package`:

```bash
    root@ubuntu-s-1vcpu-1gb-ams3:~# ls
    package
    root@ubuntu-s-1vcpu-1gb-ams3:~# ls package/
    Dockerfile  Readme.md  app  package.json
```

### Demo Executed: Deploy Node.js Application - Install Dependencies and Start the App

#### Playbook
Extended the second play with three steps:

* **Install dependencies** – the `npm` module (`community.general` collection) runs `npm install` in the app folder and creates `node_modules`.
* **Start app** – the `command` module starts the app with `node server` in the `app` folder (`chdir`). The app runs in the foreground and never ends, so without `async` the task waits forever. My first run hung at this task and I had to stop it. With `async: 1000` and `poll: 0` Ansible starts the process and continues without waiting for it.
* **Display status** – `ps aux | grep node` needs a pipe, so it runs with the `shell` module. The output is saved with `register` and printed with `debug`.

Updated playbook:

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /root/
        - name: Install dependencies
          npm:
            path: /root/package
        - name: Start app
          command:
            chdir: /root/package/app/
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
Ran the playbook. The `debug` task prints the `ps` output:

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Unpack the nodejs file] ****
    ok: [188.166.34.20]

    TASK [Install dependencies] ****
    ok: [188.166.34.20]

    TASK [Start app] ****
    changed: [188.166.34.20]

    TASK [Display status] ****
    changed: [188.166.34.20]

    TASK [debug] ****
    ok: [188.166.34.20] => {
        "msg": [
            "root        8864  0.1  5.9 618624 59028 ?        Sl   11:22   0:00 node server",
            "root        9983  0.0  0.2   2804  1972 pts/1    S+   11:32   0:00 /bin/sh -c ps aux | grep node",
            "root        9985  0.0  0.2   7080  2160 pts/1    S+   11:32   0:00 grep node"
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=9    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

`command` and `shell` tasks are not idempotent: Ansible can't know what the command changes, so they report `changed` on every run.

#### Verification on the Server
`node_modules` was created and the app is running:

```bash
    root@ubuntu-s-1vcpu-1gb-ams3:~/package# ls
    Dockerfile  Readme.md  app  node_modules  package-lock.json  package.json
    root@ubuntu-s-1vcpu-1gb-ams3:~/package# ps aux | grep node
    root        8864 11.8  6.3 618112 62808 ?        Sl   11:22   0:00 node server
```

### Demo Executed: Deploy Node.js Application - Run the App with a Dedicated Linux User

#### Playbook
Until now the app was deployed and started as `root`. To follow the least privilege principle, the app now runs with its own Linux user:

* **Create user for nodeapp** – a new play creates the user `nodeuser` with the `user` module.
* **Deploy nodejs app** – `become: True` and `become_user: nodeuser` run all tasks of this play as `nodeuser` (Ansible connects as `root` and switches the user with `sudo`). The artifact is unpacked to `/home/nodeuser` and the paths of the next tasks are adjusted.

Updated playbook:

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Create user for nodeapp
      hosts: 188.166.34.20
      tasks:
        - name: Create linux user
          user:
            name: nodeuser
            comment: node admin
            group: admin

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      become: True
      become_user: nodeuser
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: nodejs-app/nodejs-app-1.0.0.tgz
            dest: /home/nodeuser
        - name: Install dependencies
          npm:
            path: /home/nodeuser/package
        - name: Start app
          command:
            chdir: /home/nodeuser/package/app/
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
The `node server` process is now owned by `nodeuser`:

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Create linux user] ****
    changed: [188.166.34.20]

    PLAY [Deploy nodejs app] ****
    ...
    TASK [Unpack the nodejs file] ****
    changed: [188.166.34.20]

    TASK [Install dependencies] ****
    changed: [188.166.34.20]

    TASK [Start app] ****
    changed: [188.166.34.20]

    TASK [Display status] ****
    changed: [188.166.34.20]

    TASK [debug] ****
    ok: [188.166.34.20] => {
        "msg": [
            ...
            "nodeuser   10837 32.1  6.4 618064 63732 ?        Sl   11:49   0:00 node server",
            ...
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=11   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

### Demo Executed: Replace Hardcoded Values in the Node.js Playbook with Variables

#### Variables File
The app location, version, Linux user and home directory were hardcoded in several places of the playbook. I first defined them with `vars` inside the play, then moved them to a separate file, `project-vars`, so the same playbook can be used with different values. A variable can also use another variable (`user_home_dir`).

```yaml
    location: nodejs-app
    version: 1.0.0
    linux_name: nodeuser
    user_home_dir: /home/{{linux_name}}
```

#### Playbook
The plays load the file with `vars_files` and use the values with `{{ }}`. A value that starts with a variable must be in quotes, otherwise YAML reads `{` as the start of a dictionary.

```yaml
    ---
    - name: Install node and npm
      hosts: 188.166.34.20
      tasks:
        - name: Update apt repo and cache
          apt: update_cache=yes force_apt_get=yes cache_valid_time=3600
        - name: Install nodejs and npm
          apt:
            pkg:
              - nodejs
              - npm

    - name: Create user for nodeapp
      hosts: 188.166.34.20
      vars_files:
        project-vars
      tasks:
        - name: Create linux user
          user:
            name: "{{linux_name}}"
            comment: node admin
            group: admin

    - name: Deploy nodejs app
      hosts: 188.166.34.20
      become: True
      become_user: "{{linux_name}}"
      vars_files:
        project-vars
      tasks:
        - name: Unpack the nodejs file
          unarchive:
            src: "{{location}}/nodejs-app-{{version}}.tgz"
            dest: "{{user_home_dir}}"
        - name: Install dependencies
          npm:
            path: "{{user_home_dir}}/package"
        - name: Start app
          command:
            chdir: "{{user_home_dir}}/package/app/"
            cmd: node server
          async: 1000
          poll: 0
        - name: Display status
          shell: ps aux | grep node
          register: app_status
        - debug: msg={{app_status.stdout_lines}}
```

#### Execution
The result is the same as before. The user, the files and the dependencies already existed, so only the `command` and `shell` tasks report `changed`.

```bash
    (.venv) root@PC:~/modules/ansible/01-node-app# ansible-playbook -i hosts deploy-node.yaml
    ...
    TASK [Create linux user] ****
    ok: [188.166.34.20]

    PLAY [Deploy nodejs app] ****
    ...
    TASK [Unpack the nodejs file] ****
    ok: [188.166.34.20]

    TASK [Install dependencies] ****
    ok: [188.166.34.20]

    TASK [Start app] ****
    changed: [188.166.34.20]

    TASK [Display status] ****
    changed: [188.166.34.20]

    TASK [debug] ****
    ok: [188.166.34.20] => {
        "msg": [
            ...
            "nodeuser   12977  0.1  5.9 618312 58692 ?        Sl   13:00   0:00 node server",
            ...
        ]
    }

    PLAY RECAP ****
    188.166.34.20              : ok=11   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
