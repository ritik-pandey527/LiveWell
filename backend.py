import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "pandeyritik527@gmail.com"  # Replace with your email
app.config["MAIL_PASSWORD"] = "afvo ycqa cyox vlts"  # Use App Password
app.config["MAIL_DEFAULT_SENDER"] = "pandeyritik527@gmail.com"

mail = Mail(app)

# Store latest data
latest_data = {}
latest_hospitals = []

RECIPIENT_EMAIL = "pandeyritik527@gmail.com"  # Change this

def fetch_hospitals():
    """Fetch hospitals from API with fallback."""
    global latest_hospitals
    hospitals = []

    try:
        print("🔍 Fetching hospitals from API...")
        response = requests.get("https://livewell-lxau.onrender.com/get_hospitals", timeout=5)
        print(f"API Response Code: {response.status_code}")

        if response.status_code == 200:
            hospitals_data = response.json()
            print(f"🏥 Raw Hospital Data: {hospitals_data}")

            hospitals = hospitals_data.get("hospitals", [])
            if hospitals:
                latest_hospitals = hospitals  # ✅ Update stored hospitals
            else:
                print("⚠️ API returned empty hospital list, using stored data...")

    except requests.RequestException as e:
        print(f"⚠️ API Request Failed: {e}")
        hospitals = latest_hospitals  # 🔄 Use last known hospitals

    return hospitals

def send_email(to_email, x_value, y_value, z_value, hospitals):
    """Send fall alert email."""
    try:
        subject = "🚨 Fall Detected! Emergency Alert"
        hospitals_list = "<br>".join(hospitals) if hospitals else "No hospitals available."

        message_body = f"""
        <h3>🚨 Fall Detected! 🚨</h3>
        <p><b>X:</b> {x_value}</p>
        <p><b>Y:</b> {y_value}</p>
        <p><b>Z:</b> {z_value}</p>
        <p><b>Nearby Hospitals:</b></p>
        <p>{hospitals_list}</p>
        """

        msg = Message(subject=subject, recipients=[to_email], html=message_body)
        mail.send(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Email send error: {str(e)}"

@app.route('/fall_data', methods=['POST'])
def fall_data():
    """Receive fall detection data & send alert email."""
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

            hospitals = fetch_hospitals()  # Fetch hospitals
            print(f"🏥 Hospitals to be sent in email: {hospitals}")  # Debugging log

            email_status = send_email(RECIPIENT_EMAIL, x_value, y_value, z_value, hospitals)

            return jsonify({"message": "Fall detected!", "email_status": email_status}), 200

        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    """Receive and store sensor data."""
    global latest_data
    latest_data = request.get_json()
    print("📡 Received Data:", latest_data)
    return jsonify({"message": "✅ Data received successfully!"})

@app.route('/send_hospitals', methods=['POST'])
def receive_hospitals():
    """Receive and store hospital details."""
    global latest_hospitals
    try:
        data = request.json
        hospitals = data.get("hospitals", [])

        if not hospitals:
            print("⚠️ No hospitals received!")
            return jsonify({"message": "⚠️ No hospital data received"}), 400

        latest_hospitals = hospitals
        print("🏥 Updated Hospital List:", latest_hospitals)

        return jsonify({"message": "✅ Hospital data received successfully", "hospitals": latest_hospitals}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_frontend', methods=['GET'])
def get_receive_data():
    """Fetch the latest received sensor data."""
    return jsonify({"message": "📡 Data fetched successfully!", "data": latest_data})

@app.route('/fall-detect', methods=['GET'])
def fall_detect():
    """Simulate a fall detection event."""
    return jsonify({"fall_detected": True})

@app.route('/get_hospitals', methods=['GET'])
def get_hospitals():
    """Fetch stored hospitals."""
    return jsonify({"message": "Hospitals fetched successfully!", "hospitals": latest_hospitals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
