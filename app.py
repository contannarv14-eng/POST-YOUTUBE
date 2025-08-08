from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import logging
from video_processor import process_video

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a instância do Flask
app = Flask(__name__)
CORS(app)  # 👉 Libera o acesso do HTML pelo navegador (CORS)

# Rota raiz para ver se está online
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "POST-YOUTUBE API is online"}), 200

# Rota para processar vídeos
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Requisição sem corpo JSON")
            return jsonify({"error": "Missing JSON body"}), 400

        video_url = data.get("video_url")
        if not video_url:
            logger.warning("Requisição sem 'video_url'")
            return jsonify({"error": "Missing video_url"}), 400

        logger.info(f"Recebido vídeo para processamento: {video_url}")

        # Inicia o processamento em thread separada
        threading.Thread(target=process_video, args=(video_url,)).start()

        return jsonify({"status": "Processing started"}), 202

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

