import time
import subprocess

WORK_MINUTES = 25
SHORT_BREAK = 5
LONG_BREAK = 15
SESSIONS = 4

def notify(title, message):
    try: #Error handling
        subprocess.run([
            "notify-send",
            "--urgency=normal",
            "--icon=clock",
            title,
            message
            ])
    except FileNotFoundError:
        print(f"[notify] {title}: {message}") #Fall back to Terminal if notify-send is not available

def countdown(minutes, label):
    total_seconds = minutes*60
    number = 10
    
    
    while(total_seconds>0):
        
        mins = total_seconds // 60
        secs = total_seconds % 60
        display = f"{label} : {mins:02d} : {secs:02d}"
        print(display, end="\r")
        time.sleep(1)
        total_seconds -= 1
    print(f"{label} is done!")
    
def run_session(session_num):
    print(f"\n-------- Pomodoro {session_num} of {SESSIONS} -----------")
    notify("🍅 Work time!", f"Pomodoro {session_num} of {SESSIONS} starting.")
    countdown(WORK_MINUTES, "Work")
    
    if(session_num < SESSIONS):
        notify("☕ Short break", "5 minutes. Step away!")
        countdown(SHORT_BREAK, "Short Break")
    else:
        notify("🎉 Long break!", "15 minutes. You earned it.")
        countdown(LONG_BREAK,"Long Break")

def main():
    print("Pomodoro started!")
    
    for i in range(1, SESSIONS+1):
        run_session(i)
    notify("✅ All done!", "Great work today.")
    print("All sessions completed!")

main()        