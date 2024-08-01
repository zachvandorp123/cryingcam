import requests
from dotenv import load_dotenv
import os
import time

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
    sound_name="default",
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
                "push": {
                    "sound": {
                        "name": sound_name,  # The name of the sound 
                    }
                },
            },
        }

        # Send POST request to the Home Assistant notify API
        response = requests.post(url, json=data, headers=headers)
        handle_response(response)


def get_light_status():
    url = f"{api}/states/{light_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get the status: {response.status_code} {response.text}")
        return None


def strobe_lamp():
    url = f"{api}/services/light/turn_on"
    data = {"entity_id": light_name, "effect": "colorstrobe"}
    response_on = requests.post(url, json=data, headers=headers)
    handle_response(response_on)


def light_color(color):
    url = f"{api}/services/light/turn_on"
    data = {
        "entity_id": light_name,
        "color_name": color,
    }
    response_on = requests.post(url, json=data, headers=headers)
    handle_response(response_on)


def brightness(pct):
    url = f"{api}/services/light/turn_on"
    data = {
        "entity_id": light_name,
        "brightness_pct": pct,
    }
    response_on = requests.post(url, json=data, headers=headers)
    handle_response(response_on)


def sleep(duration):
    return time.sleep(duration)

def light_off():
    url = f"{api}/services/light/turn_off"
    data = {
        "entity_id": light_name,
    }
    response_off = requests.post(url, json=data, headers=headers)
    handle_response(response_off)


def light_on(color="red", brightness=100):
    url = f"{api}/services/light/turn_on"
    data = {
        "entity_id": light_name,
        "color_name": color,
        "brightness_pct": brightness
    }
    response_off = requests.post(url, json=data, headers=headers)
    handle_response(response_off)


def restore_light(state_info):
    if state_info["state"] == "on":
        data = {
            "entity_id": light_name,
            "color_name": state_info.get("attributes", {}).get("color_name", "white"),
            "brightness_pct": state_info.get("attributes", {}).get(
                "brightness_pct", 100
            ),
        }
        response_on = requests.post(
            f"{api}/services/light/turn_on", json=data, headers=headers
        )
    else:
        response_off = requests.post(
            f"{api}/services/light/turn_off",
            json={"entity_id": light_name},
            headers=headers,
        )

    handle_response(response_on if state_info["state"] == "on" else response_off)


def baby_crying_light_routine():
    initial_state = get_light_status()
    light_on()
    strobe_lamp()
    sleep(5)
    light_on("red", 10)
    sleep(60)
    light_on()
    if initial_state:
        restore_light(initial_state)
