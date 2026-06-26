import time

WORK_MINUTES = 25
SHORT_BREAK = 5
LONG_BREAK = 15
SESSIONS = 4

def countdown(minutes, label):
    total_seconds = minutes*60
    
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
    countdown(WORK_MINUTES, "Work")
    
    if(session_num < SESSIONS):
        countdown(SHORT_BREAK, "Short Break")
    else:
        countdown(LONG_BREAK,"Long Break")

def main():
    print("Pomodoro started!")
    
    for i in range(1, SESSIONS+1):
        run_session(i)
    
    print("All sessions completed!")

main()        