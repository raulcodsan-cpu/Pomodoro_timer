import time
import subprocess
import json
import argparse
# For Arguments
import csv 
# For saved metrics in csv
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

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        print("Config file is invalid, using defaults.")
        return DEFAULT_CONFIG.copy() # Can I call copy() without ()?

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Config saved to: {CONFIG_FILE}")

def parse_args(config):
    parser = argparse.ArgumentParser(description="Pomodoro timer for Linux")
    parser.add_argument("--skip", action="store_true", help="Skips one work and goes directly to short break")
    parser.add_argument("--work", type=int, default=config["work_minutes"], help="Work minutes")
    parser.add_argument("--short", type=int, default=config["short_break"], help="Short break minutes")
    parser.add_argument("--long", type=int, default=config["long_break"], help="Long break minutes")
    parser.add_argument("--sessions", type=int, default=config["sessions"], help="Sessions number")
    parser.add_argument("--save", action="store_true", help="Save settings as default")
    parser.add_argument("--stats", action="store_true", help="Show stats and exit")
    return parser.parse_args()


# ── Logging ───────────────────────────────────────────────

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


def show_stats():
    # Read the log and print a daily summary
    if not LOG_FILE.exists():
        print("No sessions logged in yet.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    totals = {}  # date → {"sessions": N, "minutes": M}

    # newline="" is added as a safety measure for Windows, that requires a parameter or else defaults to breakline.
    with open(LOG_FILE, newline="") as f:
        for row in csv.DictReader(f):
            d = row["date"]
            if d not in totals:
                totals[d] = {"sessions": 0, "minutes" : 0}
            totals[d]["sessions"] += 1
            totals[d]["minutes"] += int(row["minutes"])
    
    print("\n── Pomodoro stats ──────────────────")
    for date, data in sorted(totals.items())[-7:]:
        marker = "← today" if date == today else ""
        bar = "🍅" * data["sessions"]
        print(f"{date} {bar} ({data['sessions']} sessions, {data['minutes']} min{marker})")
    print()

# ── Timer core ────────────────────────────────────────────


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