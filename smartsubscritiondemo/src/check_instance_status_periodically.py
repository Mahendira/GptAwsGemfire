import requests
import time

# API configuration
API_URL = 'http://127.0.0.1:5000/terminate-stopped-instances'

def check_instance_status_periodically():
    while True:
        # Send GET request to the API endpoint
        response = requests.get(API_URL)
        if response.status_code == 200:
            print('Instance status checked and updated.')
        else:
            print('Failed to check instance status.')

        # Wait for 5 minutes before the next request
        # time.sleep(300)  # 5 minutes = 300 seconds
        # Wait for 5 minutes before the next request
        time.sleep(60)  # 1 minute

if __name__ == '__main__':
    check_instance_status_periodically()