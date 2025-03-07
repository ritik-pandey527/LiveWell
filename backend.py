from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

            # Log the data to a file (Optional)
            with open("fall_log.txt", "a") as log_file:
                log_file.write(f"Fall detected! X: {x_value}, Y: {y_value}, Z: {z_value}\n")

            # Additional actions (e.g., send email, push notification, database logging)
            # Example: Send Email Alert (Uncomment and configure)
            # send_email_alert(f"Fall detected! X: {x_value}, Y: {y_value}, Z: {z_value}")

        return jsonify({"message": "Data received successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received Data:", data)
    
    # Process or store the data
    return jsonify({"message": "Data received successfully!", "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
