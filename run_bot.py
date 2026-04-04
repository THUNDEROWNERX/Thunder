import subprocess
import time

def run_bot():
    while True:
        try:
            # Replace 'python3 bot.py' with the command to start your bot
            subprocess.run(['python3', 'm.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Bot crashed with exit code {e.returncode}. Restarting...")
            # Sleep for a short duration before restarting the bot
            time.sleep(3)

if __name__ == "__main__":
    run_bot()