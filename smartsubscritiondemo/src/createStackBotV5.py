from datetime import datetime
import openai
import boto3
import requests
import subprocess
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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
            return f'<div class="bot-bubble">{create_stack_response(region)}</div>'
        else:
            return "Please provide a valid region for stack creation"
    elif query.lower().startswith("aioperation"):
        response = requests.get("http://127.0.0.1:8000/monitor")
        if response.status_code == 200:
            return "Smart Subscription operation initiated"
        else:
            return "Failed to initiate Smart Subscription operation"
    elif query.lower().startswith("terminate"):
        response = requests.get("http://127.0.0.1:8000/terminateallinstances")
        if response.status_code == 200:
            return "All instances to be terminated has been initiated"
        else:
            return "Failed to initiate Smart Subscription operation"
    elif query.lower().startswith("Resize clusters created above"):
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
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=10
    )
    print(response)
    return response.choices[0].text.strip()


def create_stack_response(size):
    # Retrieve the necessary parameters from the request
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
        print("size is " + size)
        template_file = 'ApacheGeode-' + size + '.yaml'
        print("template file is " + template_file)

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
        return f"Gemfire Cluster creation initiated for size {size}. Stack ID: {response['StackId']}"
    except Exception as e:
        return f"Failed to create stack: {e}"


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
    size = request.args.get('size')
    if size:
        response = create_stack_response(size)
        # Store the current chat entry
        chat_entry = {'user_query': f"Create stack {size}", 'bot_response': response}
        chat_history.append(chat_entry)
        return redirect('/')
    else:
        return "Please provide a valid region for stack creation"


@app.route('/aioperation', methods=['GET'])
def ai_operation():
    response = query_chatbot("aioperation")
    # Store the current chat entry
    chat_entry = {'user_query': "AI Operation", 'bot_response': response}
    chat_history.append(chat_entry)
    return redirect('/')


@app.route('/terminateInstances', methods=['GET'])
def terminateInstances():
    response = query_chatbot("terminate")
    # Store the current chat entry
    chat_entry = {'user_query': "Terminate Instances", 'bot_response': response}
    chat_history.append(chat_entry)
    return redirect('/')


# @app.route('/AITiercostsavingsEstimate', methods=['GET'])
# def AITiercostsavingsEstimate():
#     response = "Here is an apporximate estimate for 1 cluster instance: <br>" \
#                "In Prod, Xtra large(226GB, Heap size per JVM) cluster costs $7000 per month, Large (110gb, Heap size per JVM) cluster costs $3500 per month.<br>" \
#                "In Test, Medium(53GB, Heap size per JVM) size cluster costs $1600 per month, Small (24gb, Heap size per JVM) costs $900 per month.<br>" \
#                "Choosing Smart subscription, just swithing to its immediate lower tier, can potentially save up to ~40% of costs when cluster is under utilized.<br>" \
#                "Reserving 10% cost for overhead cost to use Smart subscription.<br>" \
#                "1k instances can costs 7millions, smart subscription would save would save 2.5millions<br>" \
#                "only for our product expecting more than 1k instances, across many products more than 10k instances are in use, refer to dashboard in the PPT for accuracy<br>"
#
#     # Store the current chat entry
#     chat_entry = {'user_query': "AITier SavingsEstimate", 'bot_response': response}
#     chat_history.append(chat_entry)
#     return redirect('/')
@app.route('/AITiercostsavingsEstimate', methods=['GET'])
def AITiercostsavingsEstimate():
    response = "Here is an approximate estimate for one cluster instance:<br><br>" \
               "In Prod, Xtra large (226GB, Heap size per JVM) cluster costs  $7000 per month:<br>" \
               "Large (110GB, Heap size per JVM) cluster costs $3500 per month.<br><br>" \
               "In Test, Medium (53GB, Heap size per JVM) size cluster costs $1600 per month:<br>" \
               "Small (24GB, Heap size per JVM) costs $900 per month.<br><br>" \
               "By choosing the Smart subscription and switching to its immediate lower tier, you can potentially save up to ~40% of costs when the cluster is underutilized.<br>" \
               "Please reserve 10% of the cost for overhead to use the Smart subscription.<br><br>" \
               "For 1,000 instances, the cost would be 7 million, and using the Smart subscription would save approximately 2.5 million.<br>" \
               "Please note that these estimates are based on our product, and for more accurate numbers, refer to the dashboard in the presentation.<br>"

    # Store the current chat entry
    chat_entry = {'user_query': "Smart Subscription SavingsEstimate", 'bot_response': response}
    chat_history.append(chat_entry)
    return redirect('/')


if __name__ == '__main__':
    app.run()
