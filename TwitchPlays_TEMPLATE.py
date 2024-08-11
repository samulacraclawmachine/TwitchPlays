import concurrent.futures
import random
import keyboard
import pydirectinput
import pyautogui
import socket
import time
import TwitchPlays_Connection
from TwitchPlays_KeyCodes import *

##################### GAME VARIABLES #####################

# Replace this with your Twitch username. Must be all lowercase.
TWITCH_CHANNEL = 'samulacra'  # Update with your Twitch username

# If streaming on Youtube, set this to False
STREAMING_ON_TWITCH = True

# If you're streaming on Youtube, replace this with your Youtube's Channel ID
# Find this by clicking your Youtube profile pic -> Settings -> Advanced Settings
YOUTUBE_CHANNEL_ID = "YOUTUBE_CHANNEL_ID_HERE"

# If you're using an Unlisted stream to test on Youtube, replace "None" below with your stream's URL in quotes.
# Otherwise you can leave this as "None"
YOUTUBE_STREAM_URL = None

##################### MESSAGE QUEUE VARIABLES #####################

MESSAGE_RATE = 0.5
MAX_QUEUE_LENGTH = 20
MAX_WORKERS = 100  # Maximum number of threads you can process at a time

last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []
pyautogui.FAILSAFE = False

##################### ESP32 VARIABLES #####################

ESP32_IP = "192.168.0.42"  # Replace with your ESP32's IP address
PORT = 8080

def send_command_to_esp32(command):
    try:
        print(f"Attempting to connect to ESP32 at {ESP32_IP}:{PORT}...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Set a timeout for the connection attempt
            s.connect((ESP32_IP, PORT))
            print(f"Connection to ESP32 at {ESP32_IP}:{PORT} established.")
            s.sendall(command.encode('utf-8'))
            print(f"Sent command to ESP32: {command}")
            
            # Optional: Receive acknowledgment or response from ESP32
            response = s.recv(1024).decode('utf-8')
            print(f"Received from ESP32: {response}")

    except socket.timeout:
        print(f"Connection attempt to ESP32 at {ESP32_IP}:{PORT} timed out.")
    except ConnectionRefusedError:
        print(f"Connection to ESP32 at {ESP32_IP}:{PORT} refused. Is the server running?")
    except Exception as e:
        print(f"Failed to send command to ESP32: {e}")

##########################################################

# Count down before starting, so you have time to load up the game
countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
    time.sleep(1)

if STREAMING_ON_TWITCH:
    t = TwitchPlays_Connection.Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
else:
    t = TwitchPlays_Connection.YouTube()
    t.youtube_connect(YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_URL)

def handle_message(message):
    try:
        msg = message['message'].lower()
        username = message['username'].lower()

        print("Got this message from " + username + ": " + msg)

        # Send the relevant command to the ESP32
        if msg == "left": 
            send_command_to_esp32('L')
        elif msg == "right": 
            send_command_to_esp32('R')
        elif msg == "drive": 
            send_command_to_esp32('F')
        elif msg == "reverse": 
            send_command_to_esp32('B')
        elif msg == "stop": 
            send_command_to_esp32('S')
        elif msg == "up":
            send_command_to_esp32('U')
        elif msg == "down":
            send_command_to_esp32('D')

    except Exception as e:
        print("Encountered exception: " + str(e))

while True:

    active_tasks = [t for t in active_tasks if not t.done()]

    # Check for new messages
    new_messages = t.twitch_receive_messages()
    if new_messages:
        message_queue += new_messages  # New messages are added to the back of the queue
        message_queue = message_queue[-MAX_QUEUE_LENGTH:]  # Shorten the queue to only the most recent X messages

    messages_to_handle = []
    if not message_queue:
        # No messages in the queue
        last_time = time.time()
    else:
        # Determine how many messages we should handle now
        r = 1 if MESSAGE_RATE == 0 else (time.time() - last_time) / MESSAGE_RATE
        n = int(r * len(message_queue))
        if n > 0:
            # Pop the messages we want off the front of the queue
            messages_to_handle = message_queue[0:n]
            del message_queue[0:n]
            last_time = time.time()

    # If user presses Shift+Backspace, automatically end the program
    if keyboard.is_pressed('shift+backspace'):
        exit()

    if not messages_to_handle:
        continue
    else:
        for message in messages_to_handle:
            if len(active_tasks) <= MAX_WORKERS:
                active_tasks.append(thread_pool.submit(handle_message, message))
            else:
                print(f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({MAX_WORKERS}). ({len(message_queue)} messages in the queue)')