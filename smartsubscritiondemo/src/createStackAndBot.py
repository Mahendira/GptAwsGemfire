from datetime import datetime

import openai
import boto3
import requests
import subprocess
from flask import Flask, render_template, request

app = Flask(__name__)

# openai.api_key = 'YOUR_API_KEY'
openai.api_key = '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'

chat_history = []  # Initialize chat history as a global list
aws_region = "us-west-2"  # Default AWS region


def query_chatbot(query):
    # Update code to use the provided AWS region
    # You can customize this code block based on your requirements
    aws_cost_data = {
        "us-west-2": "Lowest cost in US West (Oregon) region",
        "us-east-1": "Lowest cost in US East (N. Virginia) region",
        "eu-west-1": "Lowest cost in EU (Ireland) region",
        # Add more regions as needed
    }
    if query.lower().startswith("which aws region has lowest cost"):
        region = query.lower().split(" ")[-1]
        if region in aws_cost_data:
            return aws_cost_data[region]
        else:
            return "Cost data not available for the specified region"
    elif query.lower().startswith("create stack"):
        region = query.lower().split(" ")[-1]
        if region:
            response = requests.get(f"http://localhost:5000/create-stack?region={region}")
            return response.text
        else:
            return "Please provide a valid region for stack creation"

    elif query.lower().startswith("monitor clusters created above"):
        try:
            result = subprocess.run(['python', 'check_active_connections_integrated.py'], capture_output=True,
                                    text=True)
            return result.stdout
        except Exception as e:
            return f"Failed to monitor the cluster: {e}"

    # Default response from the chatbot
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=query,
        max_tokens=50,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=10
    )
    return response.choices[0].text.strip()


@app.route('/', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        query = request.form['query']
        response = query_chatbot(query)

        # Store the current chat entry
        chat_entry = {'user_query': query, 'bot_response': response}
        chat_history.append(chat_entry)

    return render_template('index.html', chat_history=chat_history)


@app.route('/update_region', methods=['GET'])
def update_region():
    global aws_region
    region = request.args.get('region')
    if region:
        aws_region = region
    return f"AWS region updated: {aws_region}"


@app.route('/create-stack', methods=['GET'])
def create_stack():
    # Retrieve the necessary parameters from the request

    # stack_name = 'MyStacktwentynine'
    # key_pair_name = 'gemfirekey'
    # region = request.args.get('region')
    aws_access_key_id = 'AKIATEZ7EC2BSEVKNCN7'
    aws_secret_access_key = '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'
    # template_file = 'ApacheGeode-Large.yaml'

    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            # region_name=region
        )
        cloudformation = session.client('cloudformation')
        base_stack_name = 'demohack'
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        stack_name = f"{base_stack_name}-{timestamp}"
        key_pair_name = 'gemfirekey'
        template_file = 'ApacheGeode-Large.yaml'

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