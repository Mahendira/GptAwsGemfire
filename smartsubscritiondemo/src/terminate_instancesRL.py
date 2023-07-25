import boto3
import botocore
import numpy as np
import time
from flask import Flask, jsonify

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
Q_TABLE_FILE = 'q_table.npy'

# Flask application
app = Flask(__name__)


def initialize_q_table():
    return np.zeros((NUM_INSTANCES, NUM_ACTIONS))


def choose_action(state, q_table):
    if np.random.uniform(0, 1) < EXPLORATION_RATE:
        # Explore: choose a random action
        action = np.random.randint(NUM_ACTIONS)
    else:
        # Exploit: choose the action with the highest Q-value
        action = np.argmax(q_table[state])
    return action


def update_q_table(state, action, reward, next_state, q_table):
    max_q_value = np.max(q_table[next_state])
    q_table[state, action] += LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_q_value - q_table[state, action])


def save_q_table(q_table):
    np.save(Q_TABLE_FILE, q_table)


def load_q_table():
    try:
        q_table = np.load(Q_TABLE_FILE)
        return q_table
    except FileNotFoundError:
        print("Q-table file not found. Creating a new Q-table.")
        return initialize_q_table()


def get_instance_status(instance_id):
    ec2 = boto3.resource('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY)
    instance = ec2.Instance(instance_id)
    return instance.state['Name']


# def terminate_instance(instance_id):
#     ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
#     ec2.terminate_instances(InstanceIds=[instance_id])
#     print(f"Terminated instance: {instance_id}")

# def terminate_instance(instance_id):
#     ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
#                        aws_secret_access_key=AWS_SECRET_KEY)
#     instance_id_str = str(instance_id)  # Convert instance ID to string
#     ec2.terminate_instances(InstanceIds=[instance_id_str])
#     print(f"Terminated instance: {instance_id}")

# def terminate_instance(instance_id):
#     try:
#         ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
#         instance_id_str = str(instance_id)  # Convert instance ID to string
#         ec2.terminate_instances(InstanceIds=[instance_id_str])
#         print(f"Terminated instance: {instance_id}")
#     except botocore.exceptions.ParamValidationError as e:
#         print(f"Error terminating instance: {instance_id}. Invalid parameter: {e}")

def terminate_instance(instance_id):
    # Terminate the EC2 instance
    ec2_client = boto3.client('ec2')
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} terminated.")

# def terminate_instance(instance_id):
#     try:
#         ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
#         instance_id_str = str(instance_id)  # Convert instance ID to string
#         ec2.terminate_instances(InstanceIds=[str(instance_id)])  # Convert instance ID to string
#         print(f"Terminated instance: {instance_id}")
#     except botocore.exceptions.ParamValidationError as e:
#         print(f"Error terminating instance: {instance_id}. Invalid parameter: {e}")


# def terminate_instance(instance_id):
#     try:
#         ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
#         instance_id_str = str(instance_id)  # Convert instance ID to string
#         print(f"Instance ID type: {type(instance_id_str)}")  # Add this line
#         ec2.terminate_instances(InstanceIds=[instance_id_str])
#         print(f"Terminated instance: {instance_id}")
#     except botocore.exceptions.ParamValidationError as e:
#         if str(e).startswith('Invalid type for parameter InstanceIds'):
#             instance_id_str = str(instance_id)  # Convert instance ID to string
#             print(f"Instance ID type: {type(instance_id_str)}")  # Add this line
#             ec2.terminate_instances(InstanceIds=[{'InstanceId': instance_id_str}])
#             print(f"Terminated instance: {instance_id}")
#         else:
#             print(f"Error terminating instance: {instance_id}. Invalid parameter: {e}")


def check_instance_status(q_table):
    state = 0
    for step in range(NUM_INSTANCES):
        action = choose_action(state, q_table)
        reward = 1 if get_instance_status(action) == 'running' else -1
        next_state = (state + 1) % NUM_INSTANCES
        update_q_table(state, action, reward, next_state, q_table)
        state = next_state

        if action == 1 and reward == 1:
            terminate_instance(action)

        time.sleep(5)  # Delay between steps

    save_q_table(q_table)


@app.route('/instance-status', methods=['GET'])
def get_instance_status_endpoint():
    q_table = load_q_table()
    check_instance_status(q_table)
    return jsonify({'message': 'Instance status checked and updated.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
