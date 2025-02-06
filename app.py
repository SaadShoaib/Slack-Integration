from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Replace this with your actual Slack Webhook URL
# SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

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

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        return jsonify({"message": "Message sent to Slack!"})
    else:
        return jsonify({"message": "Failed to send message"}), 500

if __name__ == "__main__":
    app.run(debug=True)
