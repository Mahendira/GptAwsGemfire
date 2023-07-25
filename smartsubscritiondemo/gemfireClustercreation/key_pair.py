import boto3

# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

# EC2 instance details
instance_id = 'i-0015006fe0ccf6919'
key_pair_file_path = 'C:\\Users\\mahet\\PycharmProjects\\smartsubscritiondemo'
# Establish a session with AWS
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create an EC2 client
ec2_client = session.client('ec2')

# Retrieve the key pair name associated with the instance
response = ec2_client.describe_instances(InstanceIds=[instance_id])
key_pair_name = 'testclusterfour'

# Download the key pair material
response = ec2_client.create_key_pair(KeyName=key_pair_name)

# Save the key pair material to a file
key_material = response['KeyMaterial']
with open(key_pair_file_path, 'w') as key_file:
    key_file.write(key_material)

print(f"Key pair downloaded and saved to: {key_pair_file_path}")