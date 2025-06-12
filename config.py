import json
import os

CONFIG_FILE = "server_config.json"
ERROR_DIR = "error-files"
os.makedirs(ERROR_DIR, exist_ok=True)  # Ensure the error directory exists

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_server_settings(server_id):
    config = load_config()
    return config.get(str(server_id), {
        "timezone": "Europe/Brussels",
        "quote_time": "08:00",
        "channel_id": None,
        "interval": 24,
        "role_id": None
    })

def delete_server_settings(server_id):
    config = load_config()
    if str(server_id) in config:
        del config[str(server_id)]
        save_config(config)

def update_server_settings(server_id, key, value):
    config = load_config()
    if str(server_id) not in config:
        config[str(server_id)] = get_server_settings(server_id)
    config[str(server_id)][key] = value
    save_config(config)

def set_timezone(server_id, timezone):
    update_server_settings(server_id, "timezone", timezone)

def set_quote_time(server_id, quote_time):
    update_server_settings(server_id, "quote_time", quote_time)

def set_channel(server_id, channel_id):
    update_server_settings(server_id, "channel_id", channel_id)

def set_interval(server_id, interval):
    update_server_settings(server_id, "interval", interval)

def set_role(server_id, role_id):
    update_server_settings(server_id, "role_id", role_id)
