import time
import subprocess
import json
import csv 
# For saved metrics in csv
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from pathlib import Path
# For file path
from datetime import datetime

CONFIG_FILE = Path.home() / ".pomo_config.json"
LOG_FILE = Path.home() / "pomo_log.csv"

DEFAULT_CONFIG = {
    "work_minutes" : 25,
    "short_break" : 5,
    "long_break" : 15,
    "sessions" : 4,
}
# Dictionary syntax


# ── Helpers (unchanged from Phase 5) ─────────────────────


def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except FileNotFoundError, json.JSONDecodeError:
        print("Config file is invalid, using defaults.")
        return DEFAULT_CONFIG.copy()




def log_session(session_num, work_minutes):
    #Append 1 complete pomo to the CSV log.
    now = datetime.now()
    write_header = not LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="") as f:  # ─────────> another example of open() with different arguments.
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["date", "time", "session", "minutes"])
        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M"),
            session_num,
            work_minutes,
        ])

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



# ── GUI App ───────────────────────────────────────────────
class PomodoroApp:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.root.title("Pomodoro Timer")
        self.root.resizable(False, False)

        # State
        self.running = False
        self.stop_flag = threading.Event()
        self.current_session = 0
        self.total_seconds = 0
        self.max_secons = 0

        # StringVars - tkinter's reactive variables
        self.phase_var = tk.StringVar(value="Ready")
        self.timer_var = tk.StringVar(value="25:00")
        self.status_var = tk.StringVar(value="Press \"Start\" to begin session")

        self.build_ui()

    def build_ui(self):
        root = self.root
        root.configure(bg="#2b2b3b")
        pad = {"padx": 24, "pady": 6}


        # Pahse label e.g. "Work - 1 of 4"
        self.phase_label = tk.Label(root, textvariable=self.phase_var, bg="#2b2b3b", fg="#a78bfa", font=("Courier", 56, "bold"))
        self.timer_label.pack(**pad)

        # Big countdown display
        self.timer_label = tk.Label(root, textvariable=self.phase_var, bg="#2b2b3b", fg="#ffffff", font=("Courier", 56, "bold"))
        self.timer_label.pack(**pad)

        # Progress bar
        self.progress = ttk.Progressbar(root, length=240, mode="determinate", maximum=100)
        self.progress.pack(**pad)

        #Sessopm dots
        dot_frame = tk.Frame(root, bg="#2b2b3b")
        dot_frame.pack(pady=4)
        self.dots = []
        for _ in range(self.config["sessions"]):
            c = tk.Canvas(dot_frame, width=14, height=14, bg="#2b2b3b", highlightthickness=0)
            c.pack(side="left", padx=3)
            oval = c.create_oval(2,2,12,12, fill="#444", outline="")
            self.dots.append((c, oval))

        #Buttons
        btn_frame = tk.Frame(root, bg="#2b2b3b")
        btn_frame.pack(pady=12)

        self.start_btn = tk.Button(btn_frame, text="▶  Start", bg="#7c3aed", fg="white", font=("Helvetica",13,"bold"),
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self.start)
        self.start_btn.pack(side="left", padx=6)

        self.stop_btn = tk.Button(btn_frame, text="⏹  Stop",
            bg="#444", fg="white", font=("Helvetica",13),
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        self.reset_btn = tk.Button(btn_frame, text="↺",
            bg="#333", fg="#aaa", font=("Helvetica",13),
            relief="flat", padx=12, pady=8, cursor="hand2",
            command=self.reset)
        self.reset_btn.pack(side="left", padx=6)

        #Status line
        tk.Label(root, textvariable=self.status_var, bg="#2b2b3b", fg="#666", font=("Helvetica",10)).pack(pady=(0,16))


        # ── Timer logic ──────────────────────────────────────────

        def start(self):
            if(self.runn)

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
    
def run_session(session_num, cfg):
    print(f"\n-------- Pomodoro {session_num} of {cfg['sessions']} -----------")
    notify("🍅 Work time!", f"Pomodoro {session_num} starting.")
    
    if(not cfg['is_skipping']):
        countdown(cfg['work_minutes'], "Work")
    else:
        countdown(0, "Skipped work")
        cfg['is_skipping'] = False

    log_session(session_num, cfg["work_minutes"] ) # ─────────────────────>  logger
    
    if(session_num < cfg['sessions']):
        notify("☕ Short break", "{cfg['short_break']} minutes. Step away!")
        countdown(f"{cfg['short_break']}", "Short Break")
    else:
        notify("🎉 Long break!", "cfg['long_break'] minutes. You earned it.")
        countdown(cfg['long_break'],"Long Break")

def main():
    config = load_config()
    args = parse_args(config)

    cfg = {
        "work_minutes": args.work,
        "short_break":  args.short,
        "long_break":   args.long,
        "sessions":     args.sessions,
        "is_skipping": args.skip,
    }

    if args.stats:
        show_stats()
        return

    if args.save:
        save_config(cfg)

    print(f"Work {cfg['work_minutes']}m | Short {cfg['short_break']}m | {cfg['sessions']} sessions")
    
    for i in range(1, cfg['sessions']+1):
        run_session(i, cfg)
    notify("✅ All done!", "Great work today.")
    print("\nAll sessions completed!")

main()        