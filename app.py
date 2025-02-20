from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "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"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Meta will send a GET request to verify the webhook
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification token mismatch", 403

    elif request.method == 'POST':
        # Meta will send a POST request when a message is received
        data = request.get_json()
        print("Received webhook data:", data)

        # Extract WhatsApp message
        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if "value" in change and "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                sender_id = message["from"]
                                message_text = message.get("text", {}).get("body", "No text")

                                print(f"New message from {sender_id}: {message_text}")

        return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)
