# Website Monitoring and Recovery

**Technologies:** Python, Linode, Docker, Linux

I ran an nginx container on a Linode server and wrote a Python script that checks the website, sends an email when it is down, and restarts the container or the whole server.

## Summary
- Created a Linode server (Debian 13) with my SSH key, installed Docker from the Docker apt repository and started nginx with `docker run -d -p 8080:80 nginx`.
- I built the script in three steps (HTTP check, then email notification, then recovery). NOTES.md has every step. `monitor-website.py` in this folder is the final version (`monitor-restart-final.py` in my notes).
- `monitor_application()` sends a GET request to the website on port 8080 with `requests`:
  - status code not `200` → send an email and restart the container,
  - website not reachable (exception) → send an email, reboot the server and restart the container.
- `send_notification()` sends the email over Gmail SMTP (`smtp.gmail.com`, port 587, TLS) with a Gmail App Password.
- `restart_container()` connects to the server over SSH with `paramiko` and runs `docker start` for the nginx container.
- `restart_server_and_container()` reboots the server through the Linode API (`linode_api4`), waits until the server status is `running`, then restarts the container.
- The `schedule` package runs the check every 5 minutes. Credentials come from the environment variables `EMAIL_ADDRESS`, `EMAIL_PASSWORD` and `LINODE_TOKEN`.

## Run
```bash
pip install requests paramiko linode_api4 schedule
export EMAIL_ADDRESS=... EMAIL_PASSWORD=... LINODE_TOKEN=...
python monitor-website.py
```

## Result
I stopped the container on the server. The script got a connection error, sent the email, rebooted the server and started the container again (single run, before the scheduler was added). With the scheduler it then reported the website as up:
```
root@localhost:~# docker stop 7c20fbfa5125
7c20fbfa5125

(.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-restart-final.py
connection error.. HTTPConnectionPool(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Max retries exceeded with url: / (Caused by NewConnectionError("HTTPConnection(host='172-105-246-115.ip.linodeusercontent.com', port=8080): Failed to establish a new connection: [Errno 111] Connection refused"))
Sending an email...
Rebooting the server...
Restarting the app...
['7c20fbfa5125\n']
App restarted

(.venv) root@PC:~/modules/python-automation# /root/modules/python-automation/.venv/bin/python /root/modules/python-automation/05-web-monitoring/monitor-restart-final.py
All good!
All good!
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
