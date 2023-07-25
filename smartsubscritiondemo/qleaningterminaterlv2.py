import boto3
from datetime import datetime, timedelta
import numpy as np
from flask import json
from numpy.ma import copy

# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

# EC2 instance tag to identify instances for termination
tag_key = 'AutoTerminate'
tag_value = 'True'

# Define the threshold for no usage in seconds
no_usage_threshold = 3

# Q-learning parameters
learning_rate = 0.8
discount_factor = 0.95

# Create an EC2 client
ec2_client = boto3.client('ec2',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=aws_region)

# Get the current time
current_time = datetime.now()

# Define the Q-table
num_states = 1
num_actions = 2
Q = np.zeros((num_states, num_actions))

# Randomly initialize the state
state = np.random.randint(num_states)

# Q-learning algorithm
for _ in range(1000):  # Run 1000 episodes
    # Choose an action based on the epsilon-greedy policy
    epsilon = 0.2  # Exploration rate
    if np.random.uniform(0, 1) < epsilon:
        action = np.random.randint(num_actions)  # Explore
    else:
        action = np.argmax(Q[state])  # Exploit

    # Perform the chosen action (start/ignore)
    if action == 0:
        # Get the list of running instances
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'tag:' + tag_key, 'Values': [tag_value]},
                     {'Name': 'instance-state-name', 'Values': ['running']}]
        )
        print(response)
        # describe_response_copy = copy.deepcopy(response)
        # Create a copy of the describe_instances response
        describe_response_copy = json.loads(json.dumps(response))

        # Check if any instances are running
        if 'Reservations' in response and response['Reservations']:
            print("Instances are already running." )
        else:
            # Start the termination script
            print("Contents of describe_response_copy:")
            print(describe_response_copy)
            print(describe_response_copy)
            # Iterate through the instances and check for usage
            # for reservation in response.get('Reservations', []):
            #     for instance in reservation.get('Instances', []):
            # print("response looks like" + response)
            reservations = response.get('Reservations', [])
            print(reservations)
            for reservation in reservations:
                instances = reservation.get('Instances', [])
                print("Describing EC2 instances" + instances)
                for instance in instances:
                    instance_id = instance.get('InstanceId')

                    # instance_id = instance.get('InstanceId')

                    # Get the launch time of the instance
                    launch_time = instance.get('LaunchTime')

                    # Calculate the time difference between current time and launch time
                    time_difference = current_time - launch_time

                    # Check if the instance has been idle for the specified threshold
                    if time_difference.total_seconds() >= no_usage_threshold:
                        # Terminate the instance
                        ec2_client.terminate_instances(InstanceIds=[instance_id])
                        print(f"Terminated instance {instance_id} due to no usage for {no_usage_threshold} seconds.")
    else:
        # Ignore (do nothing)
        pass

    # Update the Q-table using the Q-learning equation
    next_state = state
    reward = 0  # No immediate reward in this case

    Q[state, action] = (1 - learning_rate) * Q[state, action] + \
                       learning_rate * (reward + discount_factor * np.max(Q[next_state]))

    # Move to the next state (always stays in the same state)
    state = next_state

# After training, let's see the learned Q-table
print("Learned Q-table:")
print(Q)