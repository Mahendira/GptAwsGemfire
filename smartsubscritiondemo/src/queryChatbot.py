# import openai
# from flask import Flask, render_template, request
#
# app = Flask(__name__)
#
# openai.api_key = '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'
#
# def query_chatbot(query):
#     response = openai.Completion.create(
#         engine='text-davinci-003',
#         prompt=query,
#         max_tokens=50,
#         temperature=0.7,
#         n=1,
#         stop=None,
#         timeout=10
#     )
#     return response.choices[0].text.strip()
#
# # @app.route('/', methods=['GET', 'POST'])
# # def chatbot():
# #     if request.method == 'POST':
# #         query = request.form['query']
# #         response = query_chatbot(query)
# #         return render_template('index.html', query=query, response=response)
# #     return render_template('index.html')
#
# @app.route('/', methods=['GET', 'POST'])
# def chatbot():
#     chat_history = []
#
#     if request.method == 'POST':
#         query = request.form['query']
#         response = query_chatbot(query)
#
#         # Store the chat history
#         chat_entry = {'user_query': query, 'bot_response': response}
#         chat_history.append(chat_entry)
#
#         return render_template('index.html', chat_history=chat_history)
#
#     return render_template('index.html', chat_history=chat_history)
#
# if __name__ == '__main__':
#     app.run()

# import openai
# from flask import Flask, render_template, request
#
# app = Flask(__name__)
#
# openai.api_key = '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'
#
# def query_chatbot(query):
#     response = openai.Completion.create(
#         engine='text-davinci-003',
#         prompt=query,
#         max_tokens=50,
#         temperature=0.7,
#         n=1,
#         stop=None,
#         timeout=10
#     )
#     return response.choices[0].text.strip()
#
# @app.route('/', methods=['GET', 'POST'])
# def chatbot():
#     chat_history = []
#
#     if request.method == 'POST':
#         query = request.form['query']
#         response = query_chatbot(query)
#
#         # Store the chat history
#         chat_entry = {'user_query': query, 'bot_response': response}
#         chat_history.append(chat_entry)
#
#         return render_template('index.html', chat_history=chat_history)
#
#     return render_template('index.html', chat_history=chat_history)
#
# if __name__ == '__main__':
#     app.run()

import openai
from flask import Flask, render_template, request

app = Flask(__name__)


openai.api_key = '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'
chat_history = []  # Initialize chat history as a global list

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

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        query = request.form['query']
        response = query_chatbot(query)

        # Store the current chat entry
        chat_entry = {'user_query': query, 'bot_response': response}
        chat_history.append(chat_entry)

    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run()