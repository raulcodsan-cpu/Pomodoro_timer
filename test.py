import json
from pathlib import Path


CONFIG_FILE = Path.home() / "test_config.json"

DEFAULT_CONFIG = {
    "work_minutes": 25,
    "short_break":  5,
    "long_break":   15,
    "sessions":     4,
}

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except FileNotFoundError:
        print("File not found")
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        print("Invalid JSON")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def main():
    config = load_config()
    print(config)

       
    config = {
        "work_minutes": 5,
        "short_break":  1,
    } 
    
    if input("Do you want to save?"):
        save_config(config)


main()