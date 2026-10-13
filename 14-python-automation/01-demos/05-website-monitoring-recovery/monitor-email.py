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

        
