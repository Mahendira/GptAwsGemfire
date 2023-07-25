import boto3

# AWS credentials
# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'

# EC2 instance details
instance_id = 'i-0cc18fcbba0d9c97b'
key_pair_name = 'testcluster'

# Establish a session with AWS
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create an EC2 client
ec2_client = session.client('ec2')

# Associate the existing key pair with the instance
response = ec2_client.associate_key_pair(
    InstanceId=instance_id,
    KeyName=key_pair_name
)

print(f"Key pair '{key_pair_name}' associated with the instance.")
# # Create an EC2 resource
# ec2_resource = session.resource('ec2')
#
# # Retrieve the EC2 instance
# instance = ec2_resource.Instance(instance_id)
#
# # Associate the existing key pair with the instance
# response = instance.associate_key_pair(KeyName=key_pair_name)
#
# print(f"Key pair '{key_pair_name}' associated with the instance.")