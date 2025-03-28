from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Twilio Configuration (Using the credentials you provided)
TWILIO_ACCOUNT_SID = "AC5a0980058d67d500c0b3a0787012c996"  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = "6309554332915ab3dd3afeba95ad0e7c"    # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = "+18566444159"     # Replace with your Twilio phone number
RECIPIENT_PHONE_NUMBER = "+919372856669" # Replace with the recipient's phone number

# Twilio Client Setup
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_phone):
    """Send fall alert SMS without location details."""
    try:
        # Compose SMS message content (without location details)
        message_body = """
        🚨 Fall Detected! 🚨
        A fall has been detected. Please check immediately.
        """

        # Send SMS via Twilio
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        return f"✅ SMS sent successfully! Message SID: {message.sid}"
    except Exception as e:
        return f"❌ SMS send error: {str(e)}"

@app.route('/fall_data', methods=['POST'])
def fall_data():
    """Endpoint to receive fall detection data and send an SMS alert."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        fall_detected = data.get("fall_detected", False)

        if fall_detected:
            print("🚨 Fall Detected!")

            # Send SMS alert (no location needed)
            sms_status = send_sms(RECIPIENT_PHONE_NUMBER)

            return jsonify({"message": "Fall detected!", "sms_status": sms_status}), 200

        return jsonify({"message": "No fall detected."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
