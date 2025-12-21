import json
import os

CONFIG_FILE = "server_config.json"

def load_config():
    """Load server configurations from file"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

def save_config(data):
    """Save server configurations to file"""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"❌ Error saving config: {e}")

def get_server_settings(server_id):
    """Get settings for a specific server with defaults"""
    config = load_config()
    return config.get(str(server_id), {
        "timezone": "Europe/Brussels",
        "quote_time": "08:00",
        "channel_id": None,
        "interval": 24,
        "role_id": None
    })

def update_server_settings(server_id, **kwargs):
    """Update specific settings for a server"""
    config = load_config()
    server_id_str = str(server_id)
    
    if server_id_str not in config:
        config[server_id_str] = get_server_settings(server_id)
    
    for key, value in kwargs.items():
        config[server_id_str][key] = value
    
    save_config(config)

def delete_server_settings(server_id):
    """Delete settings when bot leaves a server"""
    config = load_config()
    server_id_str = str(server_id)
    
    if server_id_str in config:
        del config[server_id_str]
        save_config(config)
        print(f"🗑️ Deleted config for server {server_id}")
