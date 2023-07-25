import boto3

# AWS credentials
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

# Create an EC2 resource
ec2_resource = session.resource('ec2')

# Retrieve the EC2 instance
instance = ec2_resource.Instance(instance_id)

# Terminate the existing instance
instance.terminate()

# Wait for the instance termination to complete
instance.wait_until_terminated()

# Launch a new instance with the existing key pair
new_instance = ec2_resource.create_instances(
    # ImageId='YOUR_IMAGE_ID',
    # InstanceType='YOUR_INSTANCE_TYPE',
    # KeyName=key_pair_name,
    # Add other parameters as required
    ImageId="ami-0889a44b331db0194",
    MinCount=1,
    MaxCount=1,
    InstanceType="t2.micro"
)

print("New instance launched with the existing key pair.")