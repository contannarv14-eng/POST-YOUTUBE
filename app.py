from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
from video_processor import process_video
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ==============================
# CONFIGURAÇÃO DO SERVIDOR
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permite chamadas do navegador

# ==============================
# ROTA PÁGINA INICIAL
# ==============================
@app.route("/", methods=["GET"])
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Erro ao carregar página: {str(e)}")
        return "<h1>API do YouTube está online</h1>", 200

# ==============================
# ROTA WEBHOOK PARA PROCESSAR VÍDEO
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Requisição sem corpo JSON")
            return jsonify({"error": "Missing JSON body"}), 400

        video_url = data.get("video_url")
        if not video_url:
            logger.warning("Campo 'video_url' não encontrado")
            return jsonify({"error": "Missing video_url"}), 400

        logger.info(f"🎬 Recebido vídeo para processamento: {video_url}")

        # Chama função que baixa, corta e envia para o YouTube
        result = process_video(video_url)

        if result.get("status") == "success":
            video_id = result.get("video_id")
            logger.info(f"✅ Vídeo enviado com sucesso: {video_id}")
            return jsonify({
                "status": "success",
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            }), 200
        else:
            logger.error(f"❌ Erro no processamento: {result}")
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Erro interno no webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ==============================
# ROTA TESTE OAUTH
# ==============================
@app.route("/test_oauth", methods=["GET"])
def test_oauth():
    try:
        # Detecta se está usando Secret File no Render
        token_path = "/etc/secrets/tokens.json" if os.path.exists("/etc/secrets/tokens.json") else "tokens.json"

        scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]

        creds = Credentials.from_authorized_user_file(token_path, scopes)
        youtube = build("youtube", "v3", credentials=creds)

        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()

        canal_nome = response["items"][0]["snippet"]["title"]

        return jsonify({"status": "OK", "mensagem": f"OAuth funcionando! Canal conectado: {canal_nome}"})

    except Exception as e:
        logger.error(f"Erro ao testar OAuth: {str(e)}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


# ==============================
# EXECUTAR LOCALMENTE OU NO RENDER
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # usa a porta do Render ou 5000 localmente
    app.run(host="0.0.0.0", port=port, debug=True)
