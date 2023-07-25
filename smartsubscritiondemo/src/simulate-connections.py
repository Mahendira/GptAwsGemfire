import boto3
import time
from flask import Flask, request

app = Flask(__name__)

# AWS credentials and configuration
AWS_ACCESS_KEY = 'AKIATEZ7EC2BSEVKNCN7'
AWS_SECRET_KEY = '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'
AWS_REGION = 'us-east-1'
def create_test_instance(image_id, instance_type, key_name):
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

def terminate_instance(instance_id):
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

    test_instance_id = create_test_instance(test_instance_image_id, test_instance_type, test_instance_key_name)

    print(f"Establishing connections to {target_instance_id} for 5 minutes...")
    time.sleep(300)  # Sleep for 5 minutes

    terminate_instance(test_instance_id)

    return "Connections simulation complete"

if __name__ == '__main__':
    app.run()