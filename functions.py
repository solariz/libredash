# functions.py

import requests
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')
LOCAL_TIMEZONE = config['General']['LOCAL_TIMEZONE']

def format_datetime_to_local(dt_str):
    """Convert UTC datetime string to local timezone."""
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    local_tz = ZoneInfo(LOCAL_TIMEZONE)
    return dt.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")

def get_down_devices(api_url, api_token):
    """Fetch down devices from a LibreNMS server."""
    headers = {
        "X-Auth-Token": api_token,
        "Content-Type": "application/json"
    }
    response = requests.get(f"{api_url}/devices", headers=headers, verify=False)

    if response.status_code == 200:
        devices = json.loads(response.text)["devices"]
        return [device for device in devices if device['status'] == 0]
    else:
        print(f"Error querying {api_url}: {response.status_code} - {response.text}")
        return []

def format_downtime(device):
    """Calculate and format device downtime."""
    last_polled = device.get('last_polled')
    last_discovered = device.get('last_discovered')

    # Use last_polled if available, otherwise use last_discovered
    last_seen = last_polled or last_discovered

    if not last_seen:
        return float('inf'), "Unknown"

    try:
        last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        downtime = current_time - last_seen_dt
        total_seconds = int(downtime.total_seconds())

        if total_seconds < 60:
            return total_seconds, f"{total_seconds}sec"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return total_seconds, f"{minutes}min"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return total_seconds, f"{hours}h {minutes}min"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return total_seconds, f"{days}d {hours}h"
    except (ValueError, TypeError) as e:
        print(f"Error processing last_seen time '{last_seen}': {str(e)}")
        return float('inf'), "Unknown"

