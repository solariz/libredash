# main.py

import urllib3
import configparser
import sys
import os
import argparse
import time
from jinja2 import Template
from datetime import datetime, timezone
from functions import format_datetime_to_local, get_down_devices, format_downtime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Check LibreNMS for down devices")
parser.add_argument("--html", "-H", action="store_true", help="Generate HTML output")
parser.add_argument("--infinite", "-I", action="store_true", help="Run Infinite for systemd service")
args = parser.parse_args()

# Read configuration
config = configparser.ConfigParser()
config_file = 'config.ini'

if not os.path.exists(config_file):
    print(f"Error: Configuration file '{config_file}' not found.")
    sys.exit(1)

try:
    config.read(config_file)
    # Count the number of API sources
    api_source_count = sum(1 for section in config.sections() if 'API_URL' in config[section])
    HTML_OUTPUT = config['General']['HTML_OUTPUT']
except Exception as e:
    print(f"Error reading configuration file: {str(e)}")
    sys.exit(1)

def main():
    all_down_devices = []

    # Fetch down devices from all configured LibreNMS servers
    for section in config.sections():
        if section != 'General':
            try:
                api_url = config[section]['API_URL']
                api_token = config[section]['API_TOKEN']
                down_devices = get_down_devices(api_url, api_token)
                all_down_devices.extend([(section, device) for device in down_devices])
            except KeyError as e:
                print(f"Error: Missing required configuration in section {section}. {str(e)}")

    if all_down_devices:
        devices_with_downtime = []
        for server, device in all_down_devices:
            seconds, downtime = format_downtime(device)
            device_name = device.get('display_name') or device.get('sysName') or device['hostname']
            location = device.get('location')
            if location:
                location = location.strip()
                location = '' if location.lower() == "unknown" else location
            else:
                location = ''
            device_info = {
                'server': server,
                'name': device_name,
                'id': device['device_id'],
                'downtime': downtime,
                'downtime_seconds': seconds,
                'hostname': device['hostname'],
                'last_polled': format_datetime_to_local(device.get('last_polled', 'Unknown')),
                'status_reason': device.get('status_reason', 'Unknown'),
                'location': location
            }
            devices_with_downtime.append(device_info)

            # Print device information
            print(f"Device down on {server}: {device_name} (ID: {device['device_id']}) - {downtime}")
            if location and location != device_name:
                print(f"{location}")
            print(f"Debug - Last polled: {device.get('last_polled')}, Last discovered: {device.get('last_discovered')}")
            print(f"Debug - Last ping: {device.get('last_ping')}, Current time: {datetime.now(timezone.utc)}")
            print(f"Debug - Status: {device.get('status')}, Status reason: {device.get('status_reason')}")
            print("---")

        # Sort devices by downtime (shortest first)
        devices_with_downtime.sort(key=lambda x: x['downtime_seconds'])

        if args.html:
            # Generate HTML output
            with open('template.html', 'r') as f:
                template_content = f.read()

            template = Template(template_content)
            html_output = template.render(
                devices=devices_with_downtime,
                creation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                api_source_count=api_source_count,
                ok_msg=""
            )

            with open(HTML_OUTPUT, 'w') as f:
                f.write(html_output)
            print(f"HTML output written to {HTML_OUTPUT}")
    else:
        print("No devices are currently down on any server.")
        if args.html:
            # Generate HTML output
            with open('template.html', 'r') as f:
                template_content = f.read()

            template = Template(template_content)
            html_output = template.render(
                devices=[],  # Pass None instead of an empty string
                creation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                api_source_count=api_source_count,
                ok_msg='<img src="ok.png" alt="All systems operational" />'  # Add the image path here
            )

            with open(HTML_OUTPUT, 'w') as f:
                f.write(html_output)
            print(f"HTML output written to {HTML_OUTPUT}")

if __name__ == "__main__":
    if args.infinite:
        while True:
            main()
            time.sleep(30)
    else:
        main()
