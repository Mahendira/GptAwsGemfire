from flask import Flask, request
import boto3

app = Flask(__name__)

@app.route('/create-stack', methods=['POST'])
def create_stack():
    # Retrieve the necessary parameters from the request
    stack_name = request.json['stack_name']
    key_pair_name = request.json['key_pair_name']
    aws_access_key_id = request.json['aws_access_key_id']
    aws_secret_access_key = request.json['aws_secret_access_key']
    template_file = request.json['template_file']

    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        cloudformation = session.client('cloudformation')

        with open(template_file, 'r') as f:
            template_body = f.read()

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
        return f"Stack creation initiated. Stack ID: {response['StackId']}"
    except Exception as e:
        return f"Failed to create stack: {e}"

if __name__ == '__main__':
    app.run()
