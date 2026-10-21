import os
import sys
import time

import requests

HOST_IP = os.environ["EC2_HOST"]
APP_PORT = os.environ["APP_PORT"]
IMAGE_TAG = os.environ["IMAGE_TAG"]

url = f"http://{HOST_IP}:{APP_PORT}"

for attempt in range(1, 6):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and IMAGE_TAG in response.text:
            print(f"App is running: {response.text.strip()}")
            sys.exit(0)
        print(f"Attempt {attempt}: status {response.status_code}")
    except requests.RequestException as ex:
        print(f"Attempt {attempt}: {ex}")
    time.sleep(5)

print("App did not respond correctly")
sys.exit(1)