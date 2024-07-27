import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def send_notification(message, title):
    url = f"http://{os.getenv('HOMEASSISTANT_IP_ADDRESS')}:{os.getenv('HOMEASSISTANT_PORT')}/api/services/notify/{os.getenv('NOTIFICATION_DEVICE')}"
    headers = {
        "Authorization": f"Bearer {os.getenv('HOME_ASSISTANT_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"message": message, "title": title}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification: {response.status_code} {response.text}")
