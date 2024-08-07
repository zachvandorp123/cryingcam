import requests
from dotenv import load_dotenv
import os

load_dotenv()

light_name = os.getenv("BEDROOM_LAMP_NAME")
zachs_phone = os.getenv("NOTIFICATION_DEVICE_1")
sharons_phone = os.getenv("NOTIFICATION_DEVICE_2")
api = f"http://{os.getenv('HOMEASSISTANT_IP_ADDRESS')}:{os.getenv('HOMEASSISTANT_PORT')}/api"
headers = {
    "Authorization": f"Bearer {os.getenv('HOME_ASSISTANT_TOKEN')}",
    "Content-Type": "application/json",
}

devices = [zachs_phone,
           sharons_phone
           ]

def handle_response(response):
    if response.status_code == 200:
        print("Request success")
    else:
        print(f"Request Failed - Status Code: {response.status_code}")
        try:
            error_details = response.json()
            print(f"Error Details: {error_details}")
        except ValueError:
            print(f"Response: {response.text}")

def send_notification(
    message,
    title,
    priority="high",
    sound_name="default",
    critical=1,
    volume=1.0,
    ttl=30,
):
    for device in devices:
        url = f"{api}/services/notify/{device}"
        print(url)
        # Construct the data payload with nested data structures for iOS and Android specifics
        data = {
            "message": message,
            "title": title,
            "data": {
                "ttl": ttl,
                "priority": priority,  # This is generally for Android
                "push": {
                    "sound": {
                        "name": sound_name,  # The name of the sound file
                        "critical": critical,  # For iOS to treat as critical
                        "volume": volume,  # Volume for iOS critical alerts
                    }
                },
            },
        }

        # Send POST request to the Home Assistant notify API
        response = requests.post(url, json=data, headers=headers)
        handle_response(response)