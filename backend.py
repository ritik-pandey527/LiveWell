from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# Twilio Credentials (Replace with actual credentials)
TWILIO_ACCOUNT_SID = "AC041d36897cd1805421570f12941542ff"
TWILIO_AUTH_TOKEN = "f4f9c26d06262e41ab3bffcc25b798ab"
TWILIO_PHONE_NUMBER = "+18106768345"
TO_PHONE_NUMBER = "+919324358212"

# Store latest sensor and hospital data
latest_data = {}
latest_hospitals = []

def send_sms(message):
    """Function to send an SMS using Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        return message.sid
    except Exception as e:
        return str(e)

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

            try:
                fall_response = requests.get("https://livewell-lxau.onrender.com/fall-detect")
                if fall_response.status_code == 200:
                    fall_status = fall_response.json()
                    print("Fall Detection API Response:", fall_status)
                    return jsonify({"message": "Data received and fall detected!", "fall_status": fall_status}), 200
                else:
                    return jsonify({"message": "Data received but fall detection API failed"}), 500
            except requests.RequestException as e:
                return jsonify({"message": "Data received but fall detection API request failed", "error": str(e)}), 500

        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    global latest_data
    latest_data = request.get_json()
    print("Received Data:", latest_data)
    return jsonify({"message": "Data received successfully!"})

@app.route('/send_hospitals', methods=['POST'])
def receive_hospitals():
    global latest_hospitals
    try:
        data = request.json
        hospitals = data.get("hospitals", [])

        if not hospitals:
            return jsonify({"message": "No hospital data received"}), 400

        latest_hospitals = hospitals  # Store received hospitals
        print("Received Hospitals:", latest_hospitals)

        return jsonify({"message": "Hospital data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_hospitals', methods=['GET'])
def get_hospitals():
    global latest_hospitals
    response_data = {"message": "Hospitals fetched successfully!", "hospitals": latest_hospitals}
    
    # Format the hospital data for SMS
    hospitals_text = "\n".join([f"{i+1}. {hosp}" for i, hosp in enumerate(latest_hospitals)])
    sms_message = f"Nearest Hospitals:\n{hospitals_text}" if latest_hospitals else "No hospitals available."

    # Send SMS
    sms_status = send_sms(sms_message)

    return jsonify({"message": "Hospitals fetched successfully!", "hospitals": latest_hospitals, "sms_status": sms_status})

@app.route('/receive_frontend', methods=['GET'])
def get_receive_data():
    return jsonify({"message": "Data fetched successfully!", "data": latest_data})

@app.route('/fall-detect', methods=['GET'])
def fall_detect():
    return jsonify({"fall_detected": True})  # Simulated response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
