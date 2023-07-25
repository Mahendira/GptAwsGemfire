import boto3

# AWS credentials
# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'


# EC2 instance details
instance_id = 'i-0cc18fcbba0d9c97b'

# Establish a session with AWS
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create an EC2 resource
ec2_resource = session.resource('ec2')

# Retrieve the EC2 instance
instance = ec2_resource.Instance(instance_id)

# Get the key pair name
key_pair_name = instance.key_name

# Get the instance username based on the key pair name and AMI
image = ec2_resource.Image(instance.image_id)
instance_username = 'ec2-user'  # Default username for Linux-based AMIs

if 'windows' in image.name.lower():
    instance_username = 'Administrator'

print("Instance Username:", instance_username)