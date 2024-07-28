import time
from notifications import send_notification, strobe_lamp, get_light_status


timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
message = f"Alert: Baby is crying! Detected at {timestamp}"
#get_light_status()
#send_notification(message, "Home Assistant Notification")
strobe_lamp(5)
