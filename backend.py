from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from twilio.rest import Client

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Twilio Credentials (Replace with actual credentials)
TWILIO_ACCOUNT_SID = "ACe6d35f05d4d797edc8778626dcb9b713"
TWILIO_AUTH_TOKEN = "ae6c4be8b93a83a11e88a294d93d597a"
TWILIO_PHONE_NUMBER = "+13512003314"
TO_PHONE_NUMBER = "+918291189618"

# React Frontend URL (Update with actual frontend URL)
REACT_FRONTEND_URL = "https://dashboardd-er2j.vercel.app/fall_data"  # Change if hosted elsewhere

@app.route('/fall_data', methods=['POST'])
def fall_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        fall_detected = data.get("fall_detected", False)
        x_value = data.get("x", 0.0)
        y_value = data.get("y", 0.0)
        z_value = data.get("z", 0.0)

        if fall_detected:
            print(f"🚨 Fall Detected! X: {x_value}, Y: {y_value}, Z: {z_value}")

            # Notify React Frontend
            try:
                requests.get(REACT_FRONTEND_URL)
            except requests.exceptions.RequestException as e:
                print("Failed to notify frontend:", e)

            # Log the data to a file (Optional)
            with open("fall_log.txt", "a") as log_file:
                log_file.write(f"Fall detected! X: {x_value}, Y: {y_value}, Z: {z_value}\n")

        return jsonify({"message": "Data received successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_hospitals', methods=['POST'])
def receive_hospitals():
    try:
        data = request.json
        print("Received hospital data:", data)

        # Send SMS via Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Emergency! Nearest hospital details: {data}",
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )

        return jsonify({"message": "Hospital data received and SMS sent", "sms_sid": message.sid}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
