import os
from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Load sensitive Twilio credentials from environment variables for security
TWILIO_ACCOUNT_SID = os.getenv("AC5a0980058d67d500c0b3a0787012c996")  # Ensure these are set in your environment
TWILIO_AUTH_TOKEN = os.getenv("6309554332915ab3dd3afeba95ad0e7c")  # Ensure these are set in your environment
TWILIO_PHONE_NUMBER = os.getenv("+18566444159")  # Your Twilio phone number
RECIPIENT_PHONE_NUMBER = os.getenv("+919372856669")  # The recipient's phone number

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

        # Ensure the incoming data contains 'fall_detected' field
        if not data or "fall_detected" not in data:
            return jsonify({"error": "Invalid data format. 'fall_detected' key is required."}), 400

        fall_detected = data["fall_detected"]

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
