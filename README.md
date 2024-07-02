# LibreNMS Device Alert Dashboard

## Description

This project creates a dashboard like HTML Overview for monitoring down devices across multiple LibreNMS instances. It fetches device status information from configured LibreNMS APIs, processes the data, and generates both console output and an HTML dashboard. The dashboard displays devices that are currently down, categorizing them by downtime duration and providing essential information such as device name, location, hostname, and last polled time.

## Features

- Monitors multiple LibreNMS instances simultaneously
- Categorizes devices based on downtime duration
- Generates a color-coded HTML dashboard with auto-refresh
- Provides console output for quick status checks
- Customizable alert thresholds and styling

## Requirements

- Python 3.7+
- pip (Python package installer)

## Dependencies

Install the required Python packages:

pip install requests jinja2 urllib3 configparser


## Configuration

1. Create a `config.ini` file in the project root directory with the following structure:

```ini
[General]
HTML_OUTPUT = /path/to/output/down_devices.html
LOCAL_TIMEZONE = Europe/Berlin

[LIBRE1]
API_URL = https://librenms.example.com/api/v0
API_TOKEN = your_api_token_here

[LIBRE2]
API_URL = https://librenms.another-example.com/api/v0
API_TOKEN = another_api_token_here

# Add more LibreNMS instances as needed
```

Ensure the template.html file is in the same directory as the main script.

## Usage

Run the script with:

`python main.py`
To generate the HTML dashboard, use the --html or -H flag:

`python main.py --html`
The script will output device status to the console and, if the HTML flag is used, generate an HTML dashboard at the location specified in config.ini.

## HTML Dashboard

The HTML dashboard will be generated at the path specified in the HTML_OUTPUT configuration. It auto-refreshes every 60 seconds and categorizes devices with color-coded boxes based on their downtime:

* Red (blinking): 0-20 minutes
* Dark Red: 21-60 minutes
* Indian Red: 61-240 minutes
* Crimson: 241-480 minutes
* Maroon: 481+ minutes






