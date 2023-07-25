import pytz
from flask import Flask, request, jsonify
import boto3
from datetime import datetime, timedelta
import datetime
import time

# Termination threshold (in minutes)
TERMINATION_THRESHOLD = 5

app = Flask(__name__)

# AWS credentials and configuration
AWS_ACCESS_KEY = 'AKIATEZ7EC2BSEVKNCN7'
AWS_SECRET_KEY = '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'
AWS_REGION = 'us-east-1'

# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

def get_stopped_instances():
    ec2 = boto3.resource('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    filters = [{'Name': 'instance-state-name', 'Values': ['stopped']}]
    instances = ec2.instances.filter(Filters=filters)
    return instances

def get_instance_stopped_time(instance):
    launch_time = instance.launch_time
    current_time = datetime.datetime.now(launch_time.tzinfo)
    stopped_time = current_time - launch_time
    return stopped_time.total_seconds() / 60

def terminate_instance(instance):
    ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    instance_id = instance.instance_id
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f"Terminated instance: {instance_id}")

@app.route('/terminate-stopped-instances', methods=['GET'])
def terminate_stopped_instances():
    stopped_instances = get_stopped_instances()
    terminated_instances = []

    for instance in stopped_instances:
        stopped_time = get_instance_stopped_time(instance)
        if stopped_time >= TERMINATION_THRESHOLD:
            terminate_instance(instance)
            terminated_instances.append(instance.instance_id)

    return jsonify({'terminated_instances': terminated_instances})

@app.route('/create_ec2_instance', methods=['POST'])
def create_ec2_instance():
    """
    MaxCount=1, # Keep the max count to 1, unless you have a requirement to increase it
    InstanceType="t2.micro", # Change it as per your need, But use the Free tier one
    KeyName="ec2-key" # Change it to the name of the key you have.
    :return: Creates the EC2 instance.
    """
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2")
        resource_ec2.run_instances(
            ImageId="ami-0889a44b331db0194",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            # KeyName="Windows"
            KeyName="testcluster"
            # KeyName='testclusteropenssh'
        )
        return {'Instance Id of the created instance is': str(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])}
    except Exception as e:
        print(e)

@app.route('/stop-instance', methods=['POST'])
def stop_instance():
    # Get instance ID from request body
    instance_id = request.json.get('instance_id')

    # Stop the EC2 instance
    ec2 = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = ec2.stop_instances(InstanceIds=[instance_id])

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return jsonify({'message': f'Successfully stopped instance: {instance_id}'}), 200
    else:
        return jsonify({'message': f'Failed to stop instance: {instance_id}'}), 500

@app.route('/create-instances-for-image-id', methods=['POST'])
def create_instances():
    # Specify your AWS credentials and region
    # aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
    # aws_secret_access_key = 'kFrx3qSHdq/kjfVHjItnxlVIVd0kFQsWoImFjwWn'
    # aws_region = 'us-east-1'

    # Get the EC2 image ID from the request
    image_id = request.json.get('image_id')

    # Create a Boto3 EC2 client
    ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)


    # Create a new EC2 instance using the specified image ID
    response = ec2_client.run_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1
    )

    instance_id = response['Instances'][0]['InstanceId']

    return {'instance_id': instance_id}

@app.route('/print_ec2_details', methods=['GET'])
def print_ec2_details():
    # Create an EC2 client
    ec2_client = boto3.client('ec2',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_region)

    # ec2_client = boto3.client('ec2')

    # Retrieve information about all EC2 instances
    response = ec2_client.describe_instances()

    instances_details = []

    # Iterate over the reservations (groups of instances)
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Extract and print relevant details
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            #private_ip = instance.get['PrivateIpAddress']
            state = instance['State']['Name']
            launch_time = instance['LaunchTime']
            stopped_time = None

            if state == 'stopped':
                current_time = datetime.datetime.now(launch_time.tzinfo)
                stopped_time = current_time - launch_time

            # Format stopped time
            stopped_time_str = str(stopped_time.days) + 'd ' if stopped_time else 'N/A'
            stopped_time_str += str(stopped_time.seconds // 3600) + 'h ' if stopped_time else ''
            stopped_time_str += str((stopped_time.seconds % 3600) // 60) + 'm' if stopped_time else ''

            print("Instance ID:", instance_id)
            print("Instance Type:", instance_type)
            print("Public IP:", public_ip)
            #print("Private IP:", private_ip)
            print("State:", state)
            print("Launch Time:", launch_time)
            print()

        # Add instance details to the list
        instance_details = {
            'Instance ID': instance_id,
            'Instance Type': instance_type,
            'Public IP': public_ip,
            # 'Private IP': private_ip,
            'State': state,
            'Launch Time': str(launch_time),
            'How long stopped': stopped_time_str
        }
        instances_details.append(instance_details)
    # Close the connection
    ec2_client.close()
    return instances_details

@app.route('/terminate-instances', methods=['POST'])
def terminate_instances():
    # Specify your AWS credentials and region

    #
    # aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
    # aws_secret_access_key = 'kFrx3qSHdq/kjfVHjItnxlVIVd0kFQsWoImFjwWn'
    # aws_region = 'us-east-1'

    # Get the current time
    current_time = datetime.now()

    # Assuming 'naive_datetime' is your timezone-naive datetime object
    naive_datetime = datetime(2023, 5, 1, 12, 0, 0)

    # Convert the naive_datetime to a timezone-aware datetime
    timezone = pytz.timezone('America/Chicago')  # Replace 'Your_Timezone' with your actual timezone

    # Define the threshold for no usage in minutes
    no_usage_threshold = 10  # 60 = 1 hour

    # Create a Boto3 EC2 client
    ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

    # Calculate the termination time threshold
    termination_threshold = datetime.now() - timedelta(minutes=60)

    # Retrieve all EC2 instances
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        instances.extend(reservation['Instances'])

    # Terminate instances running for more than 60 minutes
    terminated_instances = []
    for instance in instances:
        launch_time = instance['LaunchTime']
        time_difference = datetime.now(timezone) - launch_time
        # if time_difference.total_seconds() / 60 >= no_usage_threshold:
        if time_difference.total_seconds() / 60 >= no_usage_threshold and instance['State']['Name'] == 'stopped':
        # if launch_time < termination_threshold and instance['State']['Name'] == 'running':
            instance_id = instance['InstanceId']
            ec2_client.terminate_instances(InstanceIds=[instance_id])
            terminated_instances.append(instance_id)

    return {'terminated_instances': terminated_instances}

def create_test_instancetwo(image_id, instance_type, key_name):
    # Create a temporary test instance
    ec2_client = boto3.client('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f"Test instance created with ID: {instance_id}")
    return instance_id

def terminate_instancetwo(instance_id):
    # Terminate the test instance
    ec2_client = boto3.client('ec2')
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(f"Test instance {instance_id} terminated.")

@app.route('/simulate-connections', methods=['POST'])
def simulate_connections():
    target_instance_id = request.form.get('instance_id')
    test_instance_image_id = 'ami-0889a44b331db0194'
    test_instance_type = 't2.micro'
    test_instance_key_name = 'Windows'

    test_instance_id = create_test_instancetwo(test_instance_image_id, test_instance_type, test_instance_key_name)

    print(f"Establishing connections to {target_instance_id} for 5 minutes...")
    time.sleep(300)  # Sleep for 5 minutes

    terminate_instancetwo(test_instance_id)

    return "Connections simulation complete"

if __name__ == '__main__':
    app.run()
