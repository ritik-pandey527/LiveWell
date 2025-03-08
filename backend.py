from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # Import requests to make an internal GET request

app = Flask(__name__)
CORS(app)

# Store latest data (In-memory storage)
latest_data = {}

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

            # Trigger /fall-detect GET request
            fall_response = requests.get("https://livewell-lxau.onrender.com/fall-detect")  # Internal call

            # Log and return the response from /fall-detect
            if fall_response.status_code == 200:
                fall_status = fall_response.json()
                print("Fall Detection API Response:", fall_status)
                return jsonify({"message": "Data received and fall detected!", "fall_status": fall_status}), 200
            else:
                return jsonify({"message": "Data received but fall detection API failed"}), 500

        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    global latest_data
    latest_data = request.get_json()
    print("Received Data:", latest_data)
    return jsonify({"message": "Data received successfully!"})


# Endpoint to receive hospital data
@app.route('/send_hospitals', methods=['POST'])
def receive_hospitals():
    try:
        data = request.json
        hospitals = data.get("hospitals", [])

        if not hospitals:
            return jsonify({"message": "No hospital data received"}), 400

        print("Received Hospitals:", hospitals)  # Log hospitals for debugging

        return jsonify({"message": "Hospital data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/receive_frontend', methods=['GET'])
def get_receive_data():
    return jsonify({"message": "Data fetched successfully!", "data": latest_data})

@app.route('/fall-detect', methods=['GET'])
def fall_detect():
    # Simulating a fall detection response
    fall_status = {"fall_detected": True}  # Change to False for testing
    return jsonify(fall_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
