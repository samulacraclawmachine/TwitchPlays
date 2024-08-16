import time
from obswebsocket import obsws, requests, events

host = "192.168.0.43"   # Use the IP address of the machine running OBS
port = 4444             # The port you have configured for OBS WebSocket
password = "dangatang"  # The password you set in OBS WebSocket settings

# Create a WebSocket client instance
ws = obsws(host, port, password)

try:
    ws.connect()

    def update_obs_timer(text):
        ws.call(requests.SetTextGDIPlusProperties(source="Timer", text=text))

    while True:
        for countdown in range(30, 0, -1):
            update_obs_timer(f"Countdown: {countdown}s")
            time.sleep(1)

        for game_time in range(15, 0, -1):
            update_obs_timer(f"Game Time: {game_time}s")
            time.sleep(1)

except KeyboardInterrupt:
    print("Script interrupted, closing connection.")
    ws.disconnect()

except Exception as e:
    print(f"An error occurred: {e}")
    ws.disconnect()

