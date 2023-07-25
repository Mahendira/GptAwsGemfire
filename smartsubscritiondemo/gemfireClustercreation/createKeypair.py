import boto3

# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

# EC2 instance details
instance_id = 'i-0cc18fcbba0d9c97b'
key_pair_name = 'KEY_PAIR_0cc18fcbba0d9c97b'
key_pair_file_path = 'C:\\KEY_PAIR_0cc18fcbba0d9c97b.pem'

# Establish a session with AWS
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create an EC2 client
ec2_client = session.client('ec2')

# Describe the EC2 instance
response = ec2_client.describe_instances(InstanceIds=[instance_id])

# Retrieve the key pair name associated with the instance
key_pair_name = response['Reservations'][0]['Instances'][0]['KeyName']

# Create a key pair object
key_pair = ec2_client.describe_key_pairs(KeyNames=[key_pair_name])['KeyPairs'][0]

# Save the key pair material to a file
key_material = key_pair['KeyMaterial']
with open(key_pair_file_path, 'w') as key_file:
    key_file.write(key_material)

print(f"Key pair '{key_pair_name}' associated with the instance and saved to: {key_pair_file_path}")