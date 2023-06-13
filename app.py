from flask import Flask, request, jsonify
import logging
import openai
from urllib.parse import parse_qs
import json
import requests

app = Flask(__name__)

# Configure OpenAI API credentials
openai.api_key = "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"

@app.route('/', methods=['POST'])
def main():
    if request.method == 'POST':
        logging.info('Received a POST request')

        try:
            req_body = request.get_data().decode()
            logging.info(f'Request body: {req_body}')

            # Parse the request body parameters
            params = parse_qs(req_body)
            app = params.get('app', [''])[0]
            sender = params.get('sender', [''])[0]
            message = params.get('message', [''])[0]

            logging.info(f'App={app}, Sender={sender}, Message={message}')

            # Generate response using ChatGPT
            response = generate_chat_response(sender, message)

            response_data = {}
            if response:
                response_data["reply"] = response
                response_data["status"] = "success"
            else:
                response_data["reply"] = "Unable to generate a response."
                response_data["status"] = "failure"

            # Call Zapier API
            zapier_url = "https://hooks.zapier.com/hooks/catch/15590813/3hy38zl/"
            zapier_payload = {
                "app": app,
                "sender": sender,
                "message": message,
                "reply": response
            }

            try:
                response = requests.post(zapier_url, json=zapier_payload)
                # Handle the response from Zapier if needed
                # ...

                return jsonify(response_data), 200
            except requests.exceptions.RequestException as e:
                logging.error(f'Error calling Zapier API: {str(e)}')
                return 'Error calling Zapier API', 500

        except ValueError as e:
            logging.error(f'Error parsing request body: {str(e)}')
            return 'Invalid request body', 400
    else:
        logging.info('Received a request that is not a POST request')
        return 'Invalid request method', 400

def generate_chat_response(sender, message):
    # Format the input for ChatGPT
    chat_history = f"{sender}: {message}"
    prompt = f">> {chat_history}\nAI:"

    # Call the OpenAI API to generate a response
    response = openai.Completion.create(
        engine="text-davinci-003",  # Or choose another ChatGPT variant if preferred
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Extract the generated reply from the API response
    if response.choices and response.choices[0].text:
        reply = response.choices[0].text.strip().replace("\n", " ")
        return reply

    return None

if __name__ == '__main__':
    app.run()
