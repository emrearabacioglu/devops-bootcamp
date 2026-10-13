import requests

response = requests.get('http://172-105-246-115.ip.linodeusercontent.com:8080/')

if response.status_code == 200:
    print('All good!')
else:
    print('App down, fix it..')