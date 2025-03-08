import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# EmailJS Configuration (Replace with your actual details)
EMAILJS_SERVICE_ID = "service_hbhv26j"
EMAILJS_TEMPLATE_ID = "template_i10uilk"
EMAILJS_USER_ID = "uoL2gXhUchCwkqKVE"
EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"

def send_email(x_value, y_value, z_value, hospitals):
    """Function to send a fall alert email via EmailJS."""
    email_data = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_USER_ID,
        "template_params": {
            "x_value": x_value,
            "y_value": y_value,
            "z_value": z_value,
            "hospital_list": "\n".join(hospitals) if hospitals else "No hospitals available.",
        }
    }

    try:
        response = requests.post(EMAILJS_API_URL, json=email_data)
        if response.status_code == 200:
            return "Email sent successfully!"
        else:
            return f"Failed to send email: {response.text}"
    except Exception as e:
        return str(e)

@app.route('/fall_data', methods=['POST'])
def fall_data():
    """Endpoint to receive fall detection data and send an email alert."""
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

            # Fetch nearby hospitals
            hospitals_response = requests.get("https://dashboardd-er2j.vercel.app/get_hospitals")  # Assuming the same server
            hospitals = hospitals_response.json().get("hospitals", []) if hospitals_response.status_code == 200 else []

            # Send email alert
            email_status = send_email(x_value, y_value, z_value, hospitals)

            return jsonify({"message": "Fall detected!", "email_status": email_status}), 200

        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
