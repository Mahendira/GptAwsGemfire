import boto3
import random
import time

import botocore
from flask import Flask, jsonify

# AWS credentials and configuration
# AWS credentials and configuration
AWS_ACCESS_KEY = 'AKIATEZ7EC2BSEVKNCN7'
AWS_SECRET_KEY = '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'
AWS_REGION = 'us-east-1'

# Q-learning parameters
NUM_INSTANCES = 3
NUM_ACTIONS = 2
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.1
Q_TABLE_FILE = 'q_table.txt'

# Flask application
app = Flask(__name__)


def initialize_q_table():
    return [[0] * NUM_ACTIONS for _ in range(NUM_INSTANCES)]


def choose_action(state, q_table):
    valid_actions = [action for action in range(NUM_ACTIONS) if action != 0]  # Exclude action 0 (instance ID "0")
    if random.random() < EXPLORATION_RATE:
        # Explore: choose a random action
        action = random.choice(valid_actions)
    else:
        # Exploit: choose the action with the highest Q-value
        action = max(valid_actions, key=lambda x: q_table[state][x])
    return action


# def choose_action(state, q_table):
#     if random.random() < EXPLORATION_RATE:
#         # Explore: choose a random action
#         action = random.randint(0, NUM_ACTIONS - 1)
#     else:
#         # Exploit: choose the action with the highest Q-value
#         action = max(range(NUM_ACTIONS), key=lambda x: q_table[state][x])
#     return action

def update_q_table(state, action, reward, next_state, q_table):
    max_q_value = max(q_table[next_state])
    q_table[state][action] += LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_q_value - q_table[state][action])


def save_q_table(q_table):
    with open(Q_TABLE_FILE, 'w') as file:
        for row in q_table:
            file.write(' '.join(str(value) for value in row) + '\n')


def load_q_table():
    try:
        with open(Q_TABLE_FILE, 'r') as file:
            lines = file.readlines()
            q_table = [[float(value) for value in line.strip().split()] for line in lines]
        return q_table
    except FileNotFoundError:
        print("Q-table file not found. Creating a new Q-table.")
        return initialize_q_table()


def get_instance_status(instance_id):
    ec2 = boto3.resource('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY)
    instance = ec2.Instance(instance_id)
    return instance.state['Name']


def terminate_instance(instance_id):
    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                           aws_secret_access_key=AWS_SECRET_KEY)
        instance_id_str = str(instance_id)  # Convert instance ID to string
        ec2.terminate_instances(InstanceIds=[instance_id_str])
        print(f"Terminated instance: {instance_id}")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidInstanceID.Malformed':
            print(f"Error terminating instance: {instance_id}. Invalid instance ID: {instance_id_str}")
        else:
            print(f"Error terminating instance: {instance_id}. {e.response['Error']['Message']}")


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


# def terminate_instance(instance_id):
#     ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
#     ec2.terminate_instances(InstanceIds=[instance_id])
#     print(f"Terminated instance: {instance_id}")

def check_instance_status(q_table):
    state = 0
    instance_ids = get_instance_ids()
    inactive_durations = {instance_id: 0 for instance_id in instance_ids}

    for step in range(NUM_INSTANCES):
        action = choose_action(state, q_table)
        reward = 1 if get_instance_status(str(action)) == 'running' else -1
        next_state = (state + 1) % NUM_INSTANCES
        update_q_table(state, action, reward, next_state, q_table)
        state = next_state

        if action == 1 and reward == 1:
            terminate_instance(str(action))

        time.sleep(5)  # Delay between steps

    save_q_table(q_table)


@app.route('/instance-status', methods=['GET'])
def get_instance_status_endpoint():
    q_table = load_q_table()
    check_instance_status(q_table)
    return jsonify({'message': 'Instance status checked and updated.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
