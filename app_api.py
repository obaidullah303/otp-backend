from flask import Flask, request, jsonify
import json, os, requests, re

app = Flask(__name__)

# Root Endpoint Added for Health Check
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "OTP Backend API is running successfully!"})

API_KEY = "np_live_RITqag96DM9k3No9DXv-7ten5bEepMIYd-RkPuHm8Uw"
BASE_URL = "https://numberpanel.tech"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

PREMIUM_FILE = "premium_users.json"
COUNTRIES_FILE = "countries.json"
SERVICES_FILE = "services.json"

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_data(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

@app.route('/api/check_user', methods=['POST'])
def check_user():
    data = request.get_json(silent=True) or {}
    user_id = str(data.get("user_id", ""))
    users = load_data(PREMIUM_FILE)
    if user_id and user_id in users:
        return jsonify({"status": "success", "is_premium": True, "name": users[user_id]})
    return jsonify({"status": "success", "is_premium": False})

@app.route('/api/get_number', methods=['POST'])
def get_number():
    data = request.get_json(silent=True) or {}
    service = str(data.get("service", ""))
    country = str(data.get("country", ""))
    clean_code = re.sub(r'[^A-Za-z]', '', country).upper()
    
    payload = {"service": service.lower(), "country": clean_code}
    try:
        res = requests.post(f"{BASE_URL}/api/request_number", headers=HEADERS, json=payload, timeout=15)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/manage_user', methods=['POST'])
def manage_user():
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    user_id = str(data.get("user_id", ""))
    name = data.get("name", "App User")
    
    users = load_data(PREMIUM_FILE)
    if action == "add":
        users[user_id] = name
        save_data(PREMIUM_FILE, users)
        return jsonify({"message": f"User {user_id} added successfully!"})
    elif action == "delete":
        if user_id in users:
            del users[user_id]
            save_data(PREMIUM_FILE, users)
            return jsonify({"message": f"User {user_id} removed!"})
        return jsonify({"message": "User not found!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
