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
    "work_minutes" : 1,
    "short_break" : 1,
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
        self.max_seconds = 0

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
        self.phase_label.pack(pady=(20,0))

        # Big countdown display
        self.timer_label = tk.Label(root, textvariable=self.timer_var, bg="#2b2b3b", fg="#ffffff", font=("Courier", 56, "bold"))
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
        if(self.running):
            return
        self.running = True
        self.stop_flag.clear()
        self._set_status("Running")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        t = threading.Thread(target=self.run_all_sessions, daemon=True)
        t.start()
        
    def stop(self):
        self.stop_flag.set() #Signals the bg thread to quit
        self.running = False
        self._set_status("Stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
    def reset(self):
        self.stop()
        self.current_session = 0
        self.timer_var.set(f"{self.config['work_minutes']:02d}:00")
        self.phase_var.set("Ready")
        self.status_var.set("Press Start to begin")
        self.progress["value"] = 0
        self._update_dots(0)

    def run_all_sessions(self):
        # Runs in a bg thread, never touches widgets directly.
        cfg = self.config
        for i in range(1, cfg["sessions"] +1):
            if self.stop_flag.is_set():
                return
            self.current_session = 1
            self._gui_update(f"WORK · {i} of {cfg['sessions']}", "#a78bfa", i-1)
            notify("🍅 Work time!", f"Pomodoro {i} starting.")
            self._countdown(cfg["work_minutes"])
            if self.stop_flag.is_set():
                return
            log_session(i,cfg["work_minutes"])
            self._mark_dot_done(i-1)
            
            if i<cfg["sessions"]:
                self._gui_update("SHORT BREAK", "#34d399", i-1)
                notify("☕ Short break", "Step away!")
                self._countdown(cfg["short_break"])
            else:
                self._gui_update("LONG BREAK 🎉", "#60a5fa", i-1)
                notify("🎉 Long break!", "You earned it.")
                self._countdown(cfg["long_break"])
                
        if not self.stop_flag.is_set():
            self._set_status("All done! Great work.")
            messagebox.showinfo("Pomodoro", "All sessions complete! 🎉")
        self.running = False
        self.root.after(0, lambda: self.start_btn.config(state="normal"))
                
    
    def _countdown(self, minutes):
        # Tick down one minute, runs in bg.
        self.total_seconds = minutes * 60
        self.max_seconds = self.total_seconds
        while self.total_seconds > 0 and not self.stop_flag.is_set():
            m = self.total_seconds // 60
            s = self.total_seconds % 60
            pct = (1 - self.total_seconds / self.max_seconds) * 100  #---------> what?
            self.root.after(0, lambda m=m, s=s, p=pct: self._tick_ui(m,s,p))
            time.sleep(1)
            self.total_seconds -= 1
            
     # ── Thread-safe UI helpers (called via root.after) ───────
     
     
    def _tick_ui(self, mins, secs, pct):
         self.timer_var.set(f"{mins:02d}:{secs:02d}")
         self.progress["value"] = pct
         
    
    def _gui_update(self, phase, color, dot_idx):
        self.root.after(0, lambda: [
            self.phase_var.set(phase),
            self.phase_label.config(fg=color),
            self._update_dots(dot_idx)
        ])
        
    def _set_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))
        
    def _update_dots(self, active_idx):
        for i, (c, oval) in enumerate(self.dots):
            color = "#7c3aed" if i < active_idx else \
                    "#a78bfa" if i == active_idx else "#444"
            c.itemconfig(oval, fill=color)
        
    def _mark_dot_done(self, idx):
        self.root.after(0, lambda: self.dots[idx][0].itemconfig(self.dots[idx][1], fill="#7c3aed"))
        
# ── Entry point ───────────────────────────────────────────

if __name__ == "__main__":
    config = load_config()
    root   = tk.Tk()
    app    = PomodoroApp(root, config)
    root.mainloop()

