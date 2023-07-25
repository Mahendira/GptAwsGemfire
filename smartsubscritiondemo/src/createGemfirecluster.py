import boto3


def create_cloudformation_stack(stack_name, template_body, key_pair_name, aws_access_key_id, aws_secret_access_key):
    session = boto3.Session(
        aws_access_key_id='AKIATEZ7EC2BSEVKNCN7',
        aws_secret_access_key='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'
    )
    cloudformation = session.client('cloudformation')

    try:
        response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM'],
            Parameters=[
                {
                    'ParameterKey': 'KeyName',
                    'ParameterValue': key_pair_name
                }
            ]
        )
        print(f"Stack creation initiated. Stack ID: {response['StackId']}")
    except Exception as e:
        print(f"Failed to create stack: {e}")


# Example usage
if __name__ == "__main__":
    stack_name = 'MyStackeight'
    key_pair_name = 'gemfirekey'
    aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
    aws_secret_access_key = 'kFrx3qSHdq/kjfVHjItnxlVIVd0kFQsWoImFjwWn'

    with open('ApacheGeode.yaml', 'r') as f:
    #with open('ApacheGeode-Large.yaml', 'r') as f:
        template_body = f.read()

    create_cloudformation_stack(stack_name, template_body, key_pair_name, aws_access_key_id, aws_secret_access_key)
