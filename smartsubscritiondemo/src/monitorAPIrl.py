import boto3
import time
import requests
from flask import Flask

app = Flask(__name__)

# Rewards for Q-learning
REWARD_TERMINATE = -100
REWARD_NOT_TERMINATE = 10

# Q-table
q_table = {}

def get_instance_ids():
    # Retrieve the instance IDs of your EC2 instances
    # Modify this based on your setup (e.g., instance tags, filtering criteria)
    # This example assumes you have multiple running instances
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    return instance_ids

def get_active_connections(instance_id):
    # Check if the EC2 instance has active connections
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instance_status(
        InstanceIds=[instance_id],
        Filters=[{'Name': 'instance-status.status', 'Values': ['ok']}]
    )
    return len(response['InstanceStatuses'])

def terminate_instance(instance_id):
    # Terminate the EC2 instance
    ec2_client = boto3.client('ec2')
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} terminated.")

def update_q_table(state, action, reward, next_state):
    # Update Q-table using Q-learning algorithm
    learning_rate = 0.1
    discount_factor = 0.9
    current_q = q_table.get((state, action), 0)
    max_next_q = max(q_table.get((next_state, a), 0) for a in ['terminate', 'not_terminate'])
    new_q = current_q + learning_rate * (reward + discount_factor * max_next_q - current_q)
    q_table[(state, action)] = new_q

@app.route('/monitor')
def monitor():
    instance_ids = get_instance_ids()
    inactive_durations = {instance_id: 0 for instance_id in instance_ids}
    termination_threshold = 3  # 3 minutes (3 * 60 seconds)

    while True:
        for instance_id in instance_ids:
            active_connections = get_active_connections(instance_id)
            if active_connections > 1:
                inactive_durations[instance_id] = 0  # Reset the inactive duration
                print(f"Active connections to {instance_id}: {active_connections}")
                action = 'not_terminate'
            else:
                inactive_durations[instance_id] += 1
                print(f"No active connections to {instance_id}. Inactive duration: {inactive_durations[instance_id]} seconds.")
                action = 'terminate' if inactive_durations[instance_id] >= termination_threshold else 'not_terminate'

            if inactive_durations[instance_id] >= termination_threshold:
                print(f"No active connections for {termination_threshold} seconds. Terminating instance: {instance_id}")
                terminate_instance(instance_id)
                instance_ids.remove(instance_id)  # Remove terminated instance from the list
                if not instance_ids:
                    print("Switching to new cluster. Initiating new cluster with small size...")
                    # Prepare the data for the API request
                    stack_name = 'MyStackthreefourteen'
                    key_pair_name = 'gemfirekey'
                    aws_access_key_id = ''
                    aws_secret_access_key = ''
                    api_url = 'http://127.0.0.1:5000//create-stack?size=Small'
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        print("Stack creation initiated.")
                        break
                    else:
                        print("Failed to initiate stack creation.")
                    break

            # Update Q-table
            update_q_table(inactive_durations[instance_id], action, REWARD_TERMINATE if action == 'terminate' else REWARD_NOT_TERMINATE, inactive_durations[instance_id] + 1)

        if not instance_ids:
            print("No more instances to monitor. Will rerun monitoring when required.")
            break

        time.sleep(1)  # Sleep for 1 second

    return "Monitoring complete!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)