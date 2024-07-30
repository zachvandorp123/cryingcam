import time
from notifications import baby_crying_light_routine, send_notification, get_light_status


timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
message = f"Alert: Baby is crying! Detected at {timestamp}"
a = get_light_status()
print(a)
# send_notification(message, "Home Assistant Notification")
# baby_crying_light_routine()
# print(timestamp)
