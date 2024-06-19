from flask import Flask, jsonify

import schedule
import time
import threading
import requests
import os
import logging
from dotenv import load_dotenv
import sys

app = Flask(__name__)
load_dotenv()

monitors_str = os.getenv('MONITOR_URLS', '')
INTERVAL_SECONDS = int(os.getenv('INTERVAL_SECONDS', 20))  # 默认间隔时间为1分钟
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() in ['true', '1', 'yes', 'on']

if not monitors_str:
    print("Error: 'monitors' environment variable is not set or is empty.", file=sys.stderr)
    sys.exit(1)

try:
    INTERVAL_SECONDS = int(INTERVAL_SECONDS)
    if INTERVAL_SECONDS <= 0:
        raise ValueError
except ValueError:
    print("Error: 'INTERVAL_SECONDS' environment variable must be a positive integer.", file=sys.stderr)
    sys.exit(1)

MONITOR_URLS = monitors_str.split(',')
print(f"MONITORS: {MONITOR_URLS}")
print(f"INTERVAL_SECONDS: {INTERVAL_SECONDS}")
print(f"DEBUG_MODE: {DEBUG_MODE}")

logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def main():
    return 'AAStar XScheduler'


@app.route('/api/healthz', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


def check_service_status():
    for url in MONITOR_URLS:
        try:
            response = requests.get(url.strip())
            if response.status_code == 200:
                logger.debug(f"Service at {url} is up and running.")
            else:
                logger.error(f"Service at {url} is down. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error while checking service at {url}: {e}")


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Schedule the task to run every minute
schedule.every(INTERVAL_SECONDS).seconds.do(check_service_status)
# Create a separate thread to run the schedule
scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.daemon = True
scheduler_thread.start()

if __name__ == '__main__':
    print("Starting the Flask app...")
    app.run(debug=DEBUG_MODE)
