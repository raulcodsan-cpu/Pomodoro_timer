import time
import subprocess as sp
#Lets python launch external programs, same as if it was terminal.
import json
import argparse 
#Library for building CLI tools.
from pathlib import Path
#Replacement for string file path.

CONFIG_FILE = Path.home() / ".pomo_config.json"
#Build path to home directory

DEFAULT_CONFIG = {
    "work_minutes" : 25,
    "short_break" : 5,
    "long_break" : 15,
    "sessions" : 4,
}

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
        #Dict merge trick, It starts with defaults, and only replaces the keys present in the json file.
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        print("Confi file is invalid, using defaults.")
        return DEFAULT_CONFIG.copy()

def notify(title, message):
    try:
        sp.run([
            "notify-send",
            "--urgency=normal",
            "--icon=clock",
            title,
            message
        ])
    except FileNotFoundError:
        print(f"[notify]{title}: {message}") #Fallback to terminal


def countdown(minutes, label):
    total_seconds = minutes*60
    
    while(total_seconds>0):
        mins = total_seconds // 60
        secs = total_seconds % 60
        display = f"{label} : {mins:02f} : {secs:02f}"
        print(display, end="\r")
        time.sleep(1)
        total_seconds -= 1
    print(f"{label} is done!")
    
def run_session(session_num):
    print(f"\n-------- Pomodoro {session_num} of {SESSIONS} -----------")
    notify("🍅Timer started!", f" Pomodoro {session_num} of {SESSIONS} starting.")
    countdown(WORK_MINUTES, "Work")
    
    if(session_num < SESSIONS):
        notify("Short Break!", "5 Minutes to relax.")
        countdown(SHORT_BREAK, "Short Break")
    else:
        notify("🎉 Long Break!", "15 Minutes to strech legs.")
        countdown(LONG_BREAK,"Long Break")

def main():
    print("Pomodoro started!")
    
    for i in range(1, SESSIONS+1):
        run_session(i)
    
    print("✅ All sessions completed!")

main()        