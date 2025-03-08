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

# Hardcoded hospital backup
HARDCODED_HOSPITALS = [
    {"name": "Dhada Hospital", "lat": 19.6973702, "lng": 72.766104, "link": "https://www.google.com/maps?q=19.6973702,72.766104"},
    {"name": "Rural Health Training Centre & Hospital Palghar", "lat": 19.694106, "lng": 72.770565, "link": "https://www.google.com/maps?q=19.694106,72.770565"},
    {"name": "Naniwadekar Hospital", "lat": 19.696111, "lng": 72.767914, "link": "https://www.google.com/maps?q=19.696111,72.767914"},
    {"name": "Kanta Hospital", "lat": 19.697335, "lng": 72.771458, "link": "https://www.google.com/maps?q=19.697335,72.771458"},
    {"name": "Aditya Nursing Home Maternity", "lat": 19.6947827, "lng": 72.7706389, "link": "https://www.google.com/maps?q=19.6947827,72.7706389"},
    {"name": "Jeevan Jyot Eye Hospital", "lat": 19.7024818, "lng": 72.7795321, "link": "https://www.google.com/maps?q=19.7024818,72.7795321"}
]

# Replace with actual recipient email
RECIPIENT_EMAIL = "pandeyritik527@gmail.com"  # Change this

def send_email(to_email, x_value, y_value, z_value, heart_rate, spo2, body_temp, latitude, longitude):
    """Send fall alert email with health data, user's location, and hospital links."""
    try:
        subject = "🚨 Fall Detected! Emergency Alert"

        # 🔥 Create hospital list with clickable Google Maps links
        hospital_list = "".join(
            f"<p>🏥 <b>{hospital['name']}</b><br>"
            f"📍 <a href='{hospital['link']}' target='_blank'>View on Google Maps</a></p>"
            for hospital in HARDCODED_HOSPITALS
        )

        # Generate Google Maps link for user's location
        user_location_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        # Email message body
        message_body = f"""
        <h3>🚨 Fall Detected! 🚨</h3>
        <p><b>X:</b> {x_value}</p>
        <p><b>Y:</b> {y_value}</p>
        <p><b>Z:</b> {z_value}</p>

        <h3>📊 Health Data:</h3>
        <p>❤️ <b>Heart Rate:</b> {heart_rate} bpm</p>
        <p>🩸 <b>SpO2:</b> {spo2}%</p>
        <p>🌡️ <b>Body Temperature:</b> {body_temp}°C</p>

        <h3>📍 User's Location:</h3>
        <p><a href='{user_location_link}' target='_blank'>View on Google Maps</a></p>

        <h3>🏥 Nearby Hospitals:</h3>
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
        heart_rate = data.get("heart_rate", "N/A")
        spo2 = data.get("spo2", "N/A")
        body_temp = data.get("body_temp", "N/A")

        # User's last known location (Replace with dynamic GPS tracking if needed)
        latitude = 19.7060402
        longitude = 72.7819734

        print(f"🚨 Fall Detected! X: {x_value}, Y: {y_value}, Z: {z_value}")
        print(f"❤️ Heart Rate: {heart_rate} bpm, 🩸 SpO2: {spo2}%, 🌡️ Temp: {body_temp}°C")

        if fall_detected:
            # Fetch nearby hospitals (if API fails, fallback to hardcoded list)
            hospitals = []
            try:
                hospitals_response = requests.get("https://dashboardd-er2j.vercel.app/get_hospitals")
                if hospitals_response.status_code == 200:
                    hospitals_data = hospitals_response.json()
                    hospitals = hospitals_data.get("hospitals", [])
                    if not hospitals:
                        print("⚠️ No hospitals received from API! Using hardcoded list.")
            except requests.RequestException:
                print("⚠️ Hospital API request failed! Using hardcoded list.")

            # Send email alert
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
            return jsonify({"message": "⚠️ No hospital data received"}), 400

        latest_hospitals = hospitals  # Store received hospitals
        return jsonify({"message": "✅ Hospital data received successfully", "hospitals": latest_hospitals}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_hospitals', methods=['GET'])
def get_hospitals():
    return jsonify({"message": "Hospitals fetched successfully!", "hospitals": latest_hospitals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
