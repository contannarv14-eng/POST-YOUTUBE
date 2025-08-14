from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
import traceback
from video_processor import process_video

# ==============================
# CONFIGURAÇÃO DO SERVIDOR E LOGS
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permite chamadas externas

# ==============================
# ROTA PÁGINA INICIAL
# ==============================
@app.route("/", methods=["GET"])
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Erro ao carregar página inicial: {str(e)}")
        return "<h1>API do YouTube está online</h1>", 200

# ==============================
# ROTA WEBHOOK PARA PROCESSAR VÍDEO
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("📩 Requisição recebida no /webhook")
    try:
        data = request.get_json()
        logger.info(f"🔍 JSON recebido: {data}")

        if not data:
            logger.warning("⚠️ Nenhum corpo JSON encontrado na requisição")
            return jsonify({"error": "Missing JSON body"}), 400

        video_url = data.get("video_url")
        if not video_url:
            logger.warning("⚠️ Campo 'video_url' ausente")
            return jsonify({"error": "Missing video_url"}), 400

        logger.info(f"🎬 Iniciando processamento do vídeo: {video_url}")

        # Chama função principal
        result = process_video(video_url)

        logger.info(f"📦 Resultado do process_video: {result}")

        if result.get("status") == "success":
            video_id = result.get("video_id")
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"✅ Vídeo enviado com sucesso! URL: {video_link}")
            return jsonify({
                "status": "success",
                "video_id": video_id,
                "video_url": video_link
            }), 200
        else:
            logger.error(f"❌ Erro no processamento: {result}")
            return jsonify(result), 500

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"💥 Erro interno no webhook: {str(e)}\n{error_trace}")
        return jsonify({"error": "Internal server error"}), 500

# ==============================
# EXECUTAR LOCALMENTE OU NO RENDER
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Porta do Render ou local
    logger.info(f"🚀 Servidor iniciado na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
