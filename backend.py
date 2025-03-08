import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {}
latest_hospitals = []

# 🔹 EmailJS Configuration (Replace with actual details)
EMAILJS_SERVICE_ID = "service_hbhv26j"  # Replace with your EmailJS Service ID
EMAILJS_TEMPLATE_ID = "template_i10uilk"  # Replace with your EmailJS Template ID
EMAILJS_USER_ID = "uoL2gXhUchCwkqKVE"  # Replace with your EmailJS User ID
EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"

# 🔹 Recipient Email (Replace with actual recipient)
RECIPIENT_EMAIL = "pandeyritik527@gmail.com"

def send_email(to_email, x_value, y_value, z_value, hospitals):
    """Function to send a fall alert email via EmailJS."""
    email_data = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_USER_ID,
        "template_params": {
            "to_email": to_email,
            "to_name": "Ritik Pandey",  # Replace with recipient name
            "from_name": "LiveWell Alert System",
            "x_value": x_value,
            "y_value": y_value,
            "z_value": z_value,
            "hospital_list": "<br>".join(hospitals) if hospitals else "No hospitals available."
        }
    }

    try:
        response = requests.post(EMAILJS_API_URL, json=email_data)
        print("📩 EmailJS Response:", response.text)  # Debugging line

        if response.status_code == 200:
            return "✅ Email sent successfully!"
        else:
            return f"❌ Failed to send email: {response.text}"
    except Exception as e:
        return f"⚠️ Email send error: {str(e)}"

@app.route('/fall_data', methods=['POST'])
def fall_data():
    """Endpoint to receive fall detection data and send an email alert."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "❌ No data received"}), 400

        fall_detected = data.get("fall_detected", False)
        x_value = data.get("x", 0.0)
        y_value = data.get("y", 0.0)
        z_value = data.get("z", 0.0)

        if fall_detected:
            print(f"🚨 Fall Detected! X: {x_value}, Y: {y_value}, Z: {z_value}")

            # 🔹 Fetch nearby hospitals
            hospitals = []
            try:
                hospitals_response = requests.get("https://dashboardd-er2j.vercel.app/get_hospitals")
                if hospitals_response.status_code == 200:
                    hospitals = hospitals_response.json().get("hospitals", [])
            except requests.RequestException as e:
                print(f"⚠️ Hospital API request failed: {str(e)}")

            # 🔹 Send email alert
            email_status = send_email(RECIPIENT_EMAIL, x_value, y_value, z_value, hospitals)

            return jsonify({"message": "🚀 Fall detected!", "email_status": email_status}), 200

        return jsonify({"message": "✅ Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    """Endpoint to receive and store sensor data."""
    global latest_data
    latest_data = request.get_json()
    print("📡 Received Data:", latest_data)
    return jsonify({"message": "✅ Data received successfully!"})

@app.route('/send_hospitals', methods=['POST'])
def receive_hospitals():
    """Endpoint to receive and store hospital details."""
    global latest_hospitals
    try:
        data = request.json
        hospitals = data.get("hospitals", [])

        if not hospitals:
            return jsonify({"message": "⚠️ No hospital data received"}), 400

        latest_hospitals = hospitals  # Store received hospitals
        print("🏥 Received Hospitals:", latest_hospitals)

        return jsonify({"message": "✅ Hospital data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_frontend', methods=['GET'])
def get_receive_data():
    """Endpoint to fetch the latest received sensor data."""
    return jsonify({"message": "📡 Data fetched successfully!", "data": latest_data})

@app.route('/fall-detect', methods=['GET'])
def fall_detect():
    """Test API to simulate a fall detection event."""
    return jsonify({"fall_detected": True})  # Simulated response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
