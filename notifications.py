import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

light_name = "light.bulb_rgbw_6a6d9a"
api = f"http://{os.getenv('HOMEASSISTANT_IP_ADDRESS')}:{os.getenv('HOMEASSISTANT_PORT')}/api"
headers = {
    "Authorization": f"Bearer {os.getenv('HOME_ASSISTANT_TOKEN')}",
    "Content-Type": "application/json",
}

def handle_response(response_on):
    if response_on.status_code == 200:
        print("Request success")
    else:
        print(
            f"Request Failed {response_on.status_code} {response_on.text}"
        )

def send_notification(message, title):
    url = f"{api}/services/notify/{os.getenv('NOTIFICATION_DEVICE')}"
    print(url)
    data = {"message": message, "title": title}

    response = requests.post(url, json=data, headers=headers)
    handle_response(response)

def get_light_status():
    url = f"{api}/states/{light_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Status of {light_name}: {data['state']}")
        if "attributes" in data:
            print("Additional Attributes:")
            for key, value in data["attributes"].items():
                print(f"{key}: {value}")
    else:
        print(f"Failed to get the status: {response.status_code} {response.text}")

def strobe_lamp(duration):
    url = f"{api}/services/light/turn_on"
    data_on = {"entity_id": light_name, "effect": "colorstrobe",}
    response_on = requests.post(url, json=data_on, headers=headers)
    handle_response(response_on)
    time.sleep(2)
    get_light_status()

    time.sleep(duration)

    # url = f"{api}/services/light/turn_on"
    # data_on = {"entity_id": light_name, "rgb_color": [255, 0, 0], "brightness_pct": 1}
    # response_on = requests.post(url, json=data_on, headers=headers)
    # handle_response(response_on)

    # time.sleep(duration)

    url = f"{api}/services/light/turn_off"
    data_off = {
        "entity_id": light_name,
    }
    response_off = requests.post(url, json=data_off, headers=headers)
    handle_response(response_off)
