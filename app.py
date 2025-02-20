import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Token de vérification pour le webhook
VERIFY_TOKEN = "ghp_CTnXUKSDvBE8Ox74ksjRuTtsaO65Oy46p9000"

# Remplace ces valeurs par celles de ton compte WhatsApp Business API
ACCESS_TOKEN = "EAAIo3XDKfEMBO8h0z3g7Uy9d8oLhZAZBnPS9LD52QxfrAaPSu6Nf6Ntva4mT6ASRzQCIAmcEZCVqYa6xOegancUsxTGAlYwugw8PBZAWxDOsK2MQQEAKZA5rkrX2g8bSbtFSJKvCOXrpnN7QGGvnBeg62obmJKm0J59w5RBG8g7mu7mXGtoJ4ZAOqOU0OaNpXV1ZC3b0lAZD"  # Ton token d'accès à l'API WhatsApp
PHONE_NUMBER_ID = "533874146483488"  # ID de ton numéro WhatsApp Business
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

EXTERNAL_API_URL = "https://feature-8-api.yakeey.com/api/v1/backchannels/public/prompt"  # URL de l'API externe

def send_whatsapp_message(recipient_id, message):
    """
    Envoie un message à un utilisateur via l'API WhatsApp Business
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    response = requests.post(WHATSAPP_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        print(f"Message envoyé avec succès à {recipient_id}")
    else:
        print(f"Erreur lors de l'envoi : {response.json()}")

def call_external_api(message_text):
    """
    Appelle l'API externe en envoyant le message reçu sur WhatsApp et retourne la réponse.
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": message_text
    }
    
    try:
        response = requests.post(EXTERNAL_API_URL, json=data, headers=headers)
        response_data = response.json()
        
        # Extraire la réponse si elle existe
        return response_data.get("response", "Aucune réponse reçue de l'API.")
    
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API externe: {e}")
        return "Une erreur est survenue lors de la communication avec notre service."

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Vérification du webhook par WhatsApp
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification token mismatch", 403

    elif request.method == 'POST':
        # Réception des messages WhatsApp
        data = request.get_json()
        print("Received webhook data:", data)

        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if "value" in change and "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                sender_id = message["from"]
                                message_text = message.get("text", {}).get("body", "No text")

                                print(f"New message from {sender_id}: {message_text}")

                                # Appeler l'API externe avec le message reçu
                                api_response = call_external_api(message_text)

                                # Envoyer la réponse obtenue sur WhatsApp
                                send_whatsapp_message(sender_id, api_response)

        return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)
