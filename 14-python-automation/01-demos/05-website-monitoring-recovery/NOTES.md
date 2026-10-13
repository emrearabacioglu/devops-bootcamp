# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Website Monitoring and Recovery

### Demo Executed: Website Monitoring - Validate the Application Response

#### Preparation: Server on Linode
Created a Linode server with Debian 13 and added my SSH public key during creation. Installed Docker from the official Docker apt repository and started an nginx container on port `8080`.

```bash
    root@localhost:~# apt update
    root@localhost:~# apt install ca-certificates curl
    root@localhost:~# install -m 0755 -d /etc/apt/keyrings
    root@localhost:~# curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    root@localhost:~# chmod a+r /etc/apt/keyrings/docker.asc
    root@localhost:~# tee /etc/apt/sources.list.d/docker.sources <<EOF
    Types: deb
    URIs: https://download.docker.com/linux/debian
    Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
    Components: stable
    Architectures: $(dpkg --print-architecture)
    Signed-By: /etc/apt/keyrings/docker.asc
    EOF
    root@localhost:~# apt update
    root@localhost:~# apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    root@localhost:~# docker run -d -p 8080:80 nginx
    root@localhost:~# docker ps
    CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                                     NAMES
    7c20fbfa5125   nginx     "/docker-entrypoint.…"   9 seconds ago   Up 8 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   fervent_wiles
```

#### Monitoring Script
The script runs locally (WSL) and sends an HTTP GET request to the nginx website with the `requests` package. If the status code is `200`, the application is up.

```python
    import requests

    response = requests.get('http://172-105-246-115.ip.linodeusercontent.com:8080/')

    if response.status_code == 200:
        print('All good!')
    else:
        print('App down, fix it..')
```

#### Execution
The website returns `200`:
```bash
    (.venv) root@PC:~/modules/python-automation/05-web-monitoring# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-health.py
    All good!
```

### Demo Executed: Email Notification When the Website Is Down

#### Gmail Configuration
Gmail no longer supports "Less secure app access", so a normal account password can't be used for SMTP login. I enabled 2-Step Verification on my Google account and created an **App Password**, which is used only by this script.

#### Credentials as Environment Variables
The email address and the App Password are not written in the code. They are set as environment variables (`EMAIL_ADDRESS`, `EMAIL_PASSWORD`) and read in the script with `os.environ.get()`.

#### Monitoring Script with Email Notification
* `send_notification()` connects to `smtp.gmail.com` on port `587`, starts TLS, logs in and sends the email to my own address.
* An email is sent in two cases:
    * the website responds, but the status code is not `200`,
    * the website is not reachable at all (connection error, caught with `try/except`).
* In the message, the subject and the body are separated by an empty line (`\n\n`).

```python
    import requests
    import smtplib
    import os

    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    def send_notification(email_msg):

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = f"Subject: SITE DOWN\n\n{email_msg}"
            smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

    try:
        response = requests.get('http://172-105-246-115.ip.linodeusercontent.com:8080/')
        if response.status_code == 200:
            print('All good!')
        else:
            print('App down, fix it..')
            msg = f"App returned {response.status_code}, fix it!"
            send_notification(msg)

    except Exception as ex:
        print(f'connection error.. {ex}')
        msg = f"App not accessible.. fix it!"
        send_notification(msg)
```

#### Execution
Application up, then application returning a non-`200` status code:
```bash
    (.venv) root@PC:~/modules/python-automation/05-web-monitoring# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-email.py
    All good!
    (.venv) root@PC:~/modules/python-automation/05-web-monitoring# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-email.py
    App down, fix it..
```

Stopped the nginx container on the server to simulate an application crash:
```bash
    root@localhost:~# docker stop 7c20fbfa5125
    7c20fbfa5125
```

The connection is refused, the exception is caught and the email is sent:
```bash
    (.venv) root@PC:~/modules/python-automation/05-web-monitoring# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-email.py
    connection error.. HTTPConnectionPool(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError("HTTPConnection(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Failed to establish a new connection: [Errno 111] Connection refused"))
```

#### Email Notification Received
<img width="1699" height="386" alt="image" src="https://github.com/user-attachments/assets/7bb745cd-3c7b-4a81-a95d-ea35988a9aca" />

### Demo Executed: Automated Recovery - Restart Application and Reboot Server

#### Preparation
* Created a Personal Access Token in Linode and set it as an environment variable (`LINODE_TOKEN`), next to the email credentials.
* The script connects to the server with my SSH key, so the public key was added to the server's `authorized_keys`.
* Installed `paramiko` (SSH client), `linode_api4` (Linode API) and `schedule` in the virtual environment.

#### Monitoring and Recovery Script
The script from the previous demo was extended with two recovery steps and split into functions:

* `restart_container()` – connects to the server via SSH with `paramiko` and runs `docker start` for the nginx container.
* `restart_server_and_container()` – reboots the server through the Linode API (`linode_api4`). It checks the server status in a loop; when the status is `running`, it waits 10 seconds and restarts the container.
* `monitor_application()`:
    * status code is not `200` → send email + restart the container,
    * application not reachable (exception) → send email + reboot the server + restart the container.
* The `schedule` package runs `monitor_application()` every 5 minutes.

```python
    import requests
    import smtplib
    import os
    import paramiko
    import linode_api4
    import time
    import schedule

    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    LINODE_TOKEN = os.environ.get('LINODE_TOKEN')

    def send_notification(email_msg):
        print("Sending an email...")
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = f"Subject: SITE DOWN\n\n{email_msg}"
            smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

    def restart_container():
        print("Restarting the app...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(hostname='172.105.246.115', username='root', key_filename='/root/.ssh/id_rsa')
        stdin, stdout, stderr = ssh.exec_command('docker start 7c20fbfa5125')
        print(stdout.readlines())
        ssh.close()
        print('App restarted')

    def restart_server_and_container():
        #restart linode server
        print("Rebooting the server...")
        client = linode_api4.LinodeClient(LINODE_TOKEN)
        nginx_server = client.load(linode_api4.Instance, 107576750)
        nginx_server.reboot()

        #restart the app
        while True:
            nginx_server = client.load(linode_api4.Instance, 107576750)
            if nginx_server.status == 'running':
                time.sleep(10)
                restart_container()
                break

    def monitor_application():
        try:
            response = requests.get('http://172-105-246-115.ip.linodeusercontent.com:8080/')
            if response.status_code == 200:
                print('All good!')
            else:
                print('App down, fix it..')
                msg = f"App returned {response.status_code}, fix it!"
                send_notification(msg)
                restart_container()
        except Exception as ex:
            print(f'connection error.. {ex}')
            msg = f"App not accessible.. fix it!"
            send_notification(msg)
            restart_server_and_container()


    schedule.every(5).minutes.do(monitor_application)

    while True:
        schedule.run_pending()
```

#### Execution
Stopped the nginx container on the server to simulate an application crash:
```bash
    root@localhost:~# docker stop 7c20fbfa5125
    7c20fbfa5125
```

The script detected the connection error, sent the email, rebooted the server via the Linode API and started the container again over SSH (single run, before the scheduler was added):
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-restart-final.py
    connection error.. HTTPConnectionPool(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError("HTTPConnection(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Failed to establish a new connection: [Errno 111] Connection refused"))
    Sending an email...
    Rebooting the server...
    Restarting the app...
    ['7c20fbfa5125\n']
    App restarted
```

With the scheduler, the application is checked every 5 minutes:
```bash
    (.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-restart-final.py
    All good!
    All good!
```
