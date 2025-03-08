import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

# Flask-Mail Configuration (Replace with your Gmail details)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "pandeyritik527@gmail.com"  # Replace with your email
app.config["MAIL_PASSWORD"] = "afvo ycqa cyox vlts"  # Use App Password, not Gmail password
app.config["MAIL_DEFAULT_SENDER"] = "pandeyritik527@gmail.com"

mail = Mail(app)

latest_data = {}
latest_hospitals = []

HARDCODED_HOSPITALS = [
    {
        "name": "Dhada Hospital",
        "lat": 19.6973702,
        "lng": 72.766104,
        "link": "https://www.google.com/maps?q=19.6973702,72.766104"
    },
    {
        "name": "Rural Health Training Centre & Hospital Palghar",
        "lat": 19.694106,
        "lng": 72.770565,
        "link": "https://www.google.com/maps?q=19.694106,72.770565"
    },
    {
        "name": "Naniwadekar Hospital",
        "lat": 19.696111,
        "lng": 72.767914,
        "link": "https://www.google.com/maps?q=19.696111,72.767914"
    },
    {
        "name": "Kanta Hospital",
        "lat": 19.697335,
        "lng": 72.771458,
        "link": "https://www.google.com/maps?q=19.697335,72.771458"
    },
    {
        "name": "Aditya Nursing Home Maternity",
        "lat": 19.6947827,
        "lng": 72.7706389,
        "link": "https://www.google.com/maps?q=19.6947827,72.7706389"
    },
    {
        "name": "Jeevan Jyot Eye Hospital",
        "lat": 19.7024818,
        "lng": 72.7795321,
        "link": "https://www.google.com/maps?q=19.7024818,72.7795321"
    }
]

# Replace with actual recipient email
RECIPIENT_EMAIL = "pandeyritik527@gmail.com"  # Change this

def send_email(to_email, x_value, y_value, z_value, heart_rate, spo2, body_temp, latitude, longitude):
    """Send fall alert email with health values, hospital locations, and current location link."""
    try:
        subject = "🚨 Fall Detected! Emergency Alert"

        # Create hospital list with clickable Google Maps links
        hospital_list = "".join(
            f"<p>🏥 <b>{hospital['name']}</b><br>"
            f"📍 <a href='{hospital['link']}' target='_blank'>View on Google Maps</a></p>"
            for hospital in HARDCODED_HOSPITALS
        )

        # Current location Google Maps link
        location_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        # Email message body
        message_body = f"""
        <h3>🚨 Fall Detected! 🚨</h3>
        <h4>📍 Current Location:</h4>
        <p><a href='{location_link}' target='_blank'>View on Google Maps</a></p>
        <h4>🏥 Nearby Hospitals:</h4>
        {hospital_list}
        """

        msg = Message(subject=subject, recipients=[to_email], html=message_body)
        mail.send(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Email send error: {str(e)}"

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

            # Fetch health values and current location
            heart_rate = data.get("heart_rate", 0)
            spo2 = data.get("spo2", 0)
            body_temp = data.get("body_temp", 0.0)
            latitude = 19.7060402
            longitude = 72.7819734

            # Send email alert with all data
            email_status = send_email(
                RECIPIENT_EMAIL, x_value, y_value, z_value,
                heart_rate, spo2, body_temp, latitude, longitude
            )

            return jsonify({"message": "Fall detected!", "email_status": email_status}), 200

        return jsonify({"message": "Data received successfully"}), 200
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
            print("⚠️ No hospitals received!")  # Debugging Log
            return jsonify({"message": "⚠️ No hospital data received"}), 400

        latest_hospitals = hospitals  # Store received hospitals
        print("🏥 Updated Hospital List:", latest_hospitals)

        return jsonify({"message": "✅ Hospital data received successfully", "hospitals": latest_hospitals}), 200
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

@app.route('/get_hospitals', methods=['GET'])
def get_hospitals():
    return jsonify({"message": "Hospitals fetched successfully!", "hospitals": latest_hospitals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
