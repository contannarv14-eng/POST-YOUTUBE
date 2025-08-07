from flask import Flask, request, jsonify
import os, threading
from video_processor import process_video

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    video_url = data.get("video_url")
    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400
    threading.Thread(target=process_video, args=(video_url,)).start()
    return jsonify({"status": "Processing started"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)