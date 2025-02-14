from flask import Flask, render_template_string, request, jsonify
import requests
import hashlib
import hmac
import os
from time import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import traceback

client = WebClient()

app = Flask(__name__)

# Replace this with your actual Slack Webhook URL
SLACK_BOT_TOKEN = ""

slack_token = SLACK_BOT_TOKEN
client = WebClient(token=slack_token)

# HTML + JavaScript for Frontend
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send Slack Message</title>
</head>
<body>
    <h2>Send Message to Slack</h2>
    <input type="text" id="messageInput" placeholder="Enter your message" />
    <button onclick="sendMessage()">Send</button>
    <p id="response"></p>

    <script>
        function sendMessage() {
            const message = document.getElementById("messageInput").value;
            if (!message) {
                alert("Please enter a message");
                return;
            }

            fetch("/send-message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("response").innerText = data.message;
            })
            .catch(error => console.error("Error:", error));
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_template)

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"message": "Message cannot be empty"}), 400


    try:
        multiplied = multiply_input_by_2(message)
        # Check if the result is not an integer
        if not isinstance(multiplied, int):
            raise ValueError(f"Invalid input in multiply_input_by_2 function. Input was: {message}")

    except Exception as e:
        # Extracting the name, description and stacktrace of the error
        error_message = str(e)
        error_name = e.__class__.__name__
        error_description = f"{error_message}"
        stack_trace = traceback.format_exc()

        dev_user_id = "U08AQ93S59T"
        # Send the error details to Slack
        response = client.chat_postMessage(
            channel="errors",
            attachments=[{
                "color": "danger",
                "pretext": f"Hey <@{dev_user_id}>, an error occurred while processing the message.",
                "fields": [
                    {"title": "Error Name", "value": error_name, "short": True},
                    {"title": "Description", "value": error_description, "short": False},
                    {"title": "Logs", "value": "Please access the server logs for more details www.serverlogs.com", "short": False},
                    {"title": "Stack Trace", "value": f"```{stack_trace}```", "short": False}
                ],
            }]
        )
        
        return jsonify({"message": f"Error occurred. Details sent to Slack!"}), 500

    response = client.chat_postMessage(
        channel="social",
        text=f"Message processed successfully: {message}"
    )

    # if not isinstance(multiplied, int):
    #     response = client.chat_postMessage(
    #         channel="errors",
    #         text= message
    #     )
    # else:
    #     response = client.chat_postMessage(
    #         channel="social",
    #         text= message
    #     )



    # payload = {"text": message}
    # response = requests.post(SLACK_WEBHOOK_URL, json=payload)
 

    if response.status_code == 200:
        return jsonify({"message": "Message sent to Slack!"})
    else:
        return jsonify({"message": "Failed to send message"}), 500

def multiply_input_by_2(input):
    try:
        input_int = int(input)
        
        multiplied_by_2 = input_int * 2
        return multiplied_by_2
    except ValueError:
        return "Error: Input must be a valid integer"

if __name__ == "__main__":
    app.run(debug=True)

# Simualte an error in the app
# Send that error to the "errors" channel
# Name, description, and stacktrace
# Format the stacktrace as a codeblock