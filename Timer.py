import time
from obswebsocket import obsws, requests, events, exceptions

host = "localhost"
port = 4444
password = "dangatang"

# Create a WebSocket client instance
ws = obsws(host, port, password)

try:
    ws.connect()

    def update_obs_timer(text):
        ws.call(requests.SetTextGDIPlusProperties(source="Timer", text=text))

    while True:
        # Countdown sequence (e.g., 30 seconds)
        for countdown in range(30, 0, -1):
            update_obs_timer(f"Countdown: {countdown} s")
            time.sleep(1)

        # Game sequence (e.g., 15 seconds)
        for game_time in range(15, 0, -1):
            update_obs_timer(f"Game Time: {game_time} s")
            time.sleep(1)

except exceptions.ConnectionFailure as e:
    print(f"Failed to connect to OBS WebSocket: {e}")

except KeyboardInterrupt:
    print("Script interrupted, closing connection.")

finally:
    try:
        ws.disconnect()
    except AttributeError:
        pass  # Handle the case where disconnect might fail
    except Exception as e:
        print(f"An error occurred during disconnect: {e}")
