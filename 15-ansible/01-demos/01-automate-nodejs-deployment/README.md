# Automate Node.js application Deployment

**Technologies:** Ansible, Node.js, DigitalOcean, Linux

I wrote an Ansible playbook that installs Node.js and npm on a DigitalOcean droplet, creates a Linux user for the app and deploys and starts the Node.js app with that user.

## Summary
1. Created an Ubuntu droplet on DigitalOcean and added its IP to the `hosts` inventory file (SSH key, user `root`, Python interpreter). `ansible.cfg` turns off host key checking.
2. Packaged the app in `nodejs-app/` with `npm pack` into `nodejs-app-1.0.0.tgz`. The `.tgz` is not in the repo (`*.tgz` is in `.gitignore`).
3. `deploy-node.yaml` has three plays:
   - **Install node and npm**: updates the apt cache and installs `nodejs` and `npm`.
   - **Create user for nodeapp**: creates the Linux user `nodeuser`.
   - **Deploy nodejs app**: runs as `nodeuser` (`become_user`). `unarchive` copies the artifact to the server and unpacks it in the user's home, the `npm` module installs the dependencies, `command` starts `node server`, and `ps aux | grep node` is printed with `register` + `debug`.
4. The app never ends, so my first run hung at the start task. With `async: 1000` and `poll: 0` Ansible starts it and goes on.
5. Moved the hardcoded values (app location, version, user, home dir) to a `project-vars` file that the plays load with `vars_files`. `project-vars` is in `.gitignore`, so it is not in the repo. Its content:
   ```yaml
   location: nodejs-app
   version: 1.0.0
   linux_name: nodeuser
   user_home_dir: /home/{{linux_name}}
   ```

## Run
```bash
ansible-playbook -i hosts deploy-node.yaml
```

## Result
Last run with `project-vars`: the user and files already exist (`ok`), and `node server` runs as `nodeuser`:
```
TASK [Create linux user] ****
ok: [188.166.34.20]
...
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

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
