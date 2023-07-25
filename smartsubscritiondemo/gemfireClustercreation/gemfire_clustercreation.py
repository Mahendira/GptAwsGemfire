import boto3
import paramiko

# AWS credentials and region
aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
aws_secret_access_key = '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'
aws_region = 'us-east-1'


# EC2 instance details
instance_id = 'i-071bdadb09f215ec4'
instance_username = 'ec2_user'
# ssh -i "testcluster.pem" ec2-user@ec2-44-211-61-5.compute-1.amazonaws.com
key_pair_file = 'C:\\Users\\mahet\\Documents\\AWSStudy\\keypair\\testclusteropenssh.pem'

# YAML file URL
yaml_file_url = 'https://raw.githubusercontent.com/haddad88/Gemfire-Apache/main/ApacheGeode.yaml'

# Establish a session with AWS
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create an EC2 client
ec2_client = session.client('ec2')

# Get the public IP address of the EC2 instance
response = ec2_client.describe_instances(InstanceIds=[instance_id])
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
print(public_ip)
print(key_pair_file)

# Connect to the EC2 instance using SSH
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(
    hostname=public_ip,
    username=instance_username,
    key_filename=key_pair_file
)

# Download the YAML file
stdin, stdout, stderr = ssh_client.exec_command(f'curl -O {yaml_file_url}')
stdout.channel.recv_exit_status()

# Deploy the YAML file using kubectl
stdin, stdout, stderr = ssh_client.exec_command('kubectl apply -f ApacheGeode.yaml')
stdout.channel.recv_exit_status()

# Close the SSH connection
ssh_client.close()