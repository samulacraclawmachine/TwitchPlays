import concurrent.futures
import random
import keyboard
import pydirectinput
import pyautogui
import socket
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
PORT = 80

def send_data_to_esp32(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ESP32_IP, PORT))
            s.sendall(data.encode('utf-8'))
            print(f"Sent data to ESP32: {data}")
    except Exception as e:
        print(f"Failed to send data to ESP32: {e}")

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

        # Send the message to the ESP32
        send_data_to_esp32(msg)

        # Now that you have a chat message, this is where you add your game logic.
        # Use the "HoldKey(KEYCODE)" function to permanently press and hold down a key.
        # Use the "ReleaseKey(KEYCODE)" function to release a specific keyboard key.
        # Use the "HoldAndReleaseKey(KEYCODE, SECONDS)" function press down a key for X seconds, then release it.
        # Use the pydirectinput library to press or move the mouse

        # I've added some example videogame logic code below:

        ###################################
        # Example GTA V Code 
        ###################################

        # If the chat message is "left", then hold down the A key for 2 seconds
        if msg == "left": 
            HoldAndReleaseKey(A, 2)

        # If the chat message is "right", then hold down the D key for 2 seconds
        if msg == "right": 
            HoldAndReleaseKey(D, 2)

        # If message is "drive", then permanently hold down the W key
        if msg == "drive": 
            ReleaseKey(S)  # release brake key first
            HoldKey(W)  # start permanently driving

        # If message is "reverse", then permanently hold down the S key
        if msg == "reverse": 
            ReleaseKey(W)  # release drive key first
            HoldKey(S)  # start permanently reversing

        # Release both the "drive" and "reverse" keys
        if msg == "stop": 
            ReleaseKey(W)
            ReleaseKey(S)

        # Press the spacebar for 0.7 seconds
        if msg == "brake": 
            HoldAndReleaseKey(SPACE, 0.7)

        # Press the left mouse button down for 1 second, then release it
        if msg == "shoot": 
            pydirectinput.mouseDown(button="left")
            time.sleep(1)
            pydirectinput.mouseUp(button="left")

        # Move the mouse up by 30 pixels
        if msg == "aim up":
            pydirectinput.moveRel(0, -30, relative=True)

        # Move the mouse right by 200 pixels
        if msg == "aim right":
            pydirectinput.moveRel(200, 0, relative=True)

        ####################################
        ####################################

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