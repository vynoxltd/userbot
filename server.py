from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)

@app.route("/demo-capture", methods=["POST"])
def capture():
    data = request.json

    username = data.get("username")
    pw_len = data.get("password_length")

    print("⚠️ PHISHING DEMO EVENT")
    print(f"Username entered: {username}")
    print(f"Password: {'*' * pw_len} (length: {pw_len})")
    print(f"Time: {time.ctime()}")

    # Here you could forward this to Telegram bot (safe message)
    return jsonify({"status": "logged"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
