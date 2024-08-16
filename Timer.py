import time
import obswebsocket
from obswebsocket import obsws, requests

host = "localhost"
port = 4444
password = "dangatang"

ws = obsws(host, port, password)
ws.connect()

def update_obs_timer(text):
    ws.call(requests.SetTextGDIPlusProperties(source="Timer", text=text))

try:
    while True:
        # Simulate receiving the countdown time from ESP32
        for countdown in range(30, 0, -1):
            update_obs_timer(f"Countdown: {countdown}s")
            time.sleep(1)

        # Simulate game sequence timing
        for game_time in range(15, 0, -1):
            update_obs_timer(f"Game Time: {game_time}s")
            time.sleep(1)

except KeyboardInterrupt:
    ws.disconnect()

