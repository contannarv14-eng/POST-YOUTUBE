from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from video_processor import process_video

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Libera o acesso do HTML pelo navegador (CORS)

# Página inicial com interface HTML
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Webhook para processar vídeos
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

        # Processa o vídeo e aguarda o retorno
        result = process_video(video_url)

        if result.get("status") == "success":
            video_id = result.get("video_id")
            return jsonify({
                "status": "success",
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            }), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Executa localmente
if __name__ == "__main__":
    app.run(debug=True)
