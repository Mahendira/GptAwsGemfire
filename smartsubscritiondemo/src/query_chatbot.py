import openai
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

openai.api_key = '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'

def query_chatbot(query):
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

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    query = data['query']
    response = query_chatbot(query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run()