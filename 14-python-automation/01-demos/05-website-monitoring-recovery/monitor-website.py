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