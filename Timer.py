import time

def countdown_timer(start_time, interval):
    while True:
        # Countdown phase
        current_time = start_time
        while current_time >= 0:
            minutes, seconds = divmod(current_time, 60)
            time_str = f"{minutes:02}:{seconds:02}"

            with open("countdown.txt", "w") as file:
                file.write(time_str)
            
            time.sleep(1)
            current_time -= 1
        
        # Interval phase
        current_time = interval
        while current_time >= 0:
            minutes, seconds = divmod(current_time, 60)
            interval_str = f"Next Round in {minutes:02}:{seconds:02}"

            with open("countdown.txt", "w") as file:
                file.write(interval_str)
            
            time.sleep(1)
            current_time -= 1

if __name__ == "__main__":
    start_time = 5 * 60  # 5 minutes countdown
    interval = 10  # 10 seconds interval countdown
    countdown_timer(start_time, interval)
