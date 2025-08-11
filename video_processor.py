import os
import yt_dlp
import subprocess
import glob
import time
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==============================
# CONFIGURAÇÃO DE LOG
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def get_youtube_service():
    creds = Credentials(
        token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('youtube', 'v3', credentials=creds)


def process_video(
    youtube_url,
    start_time="00:00:00",
    duration="00:01:00",
    title="Short automático",
    description="Gerado automaticamente",
    max_retries=3,
    sleep_seconds=10
):
    try:
        # ==============================
        # 0. NORMALIZAR LINK DE SHORTS
        # ==============================
        if "youtube.com/shorts/" in youtube_url:
            logger.info("🔗 Link de Shorts detectado. Convertendo para formato padrão...")
            youtube_url = youtube_url.replace("youtube.com/shorts/", "youtube.com/watch?v=")

        logger.info(f"🎯 Link final para download: {youtube_url}")

        # ==============================
        # 1. BAIXAR VÍDEO DO YOUTUBE
        # ==============================
        ydl_opts = {
            'outtmpl': 'input_video.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        attempt = 0
        while attempt < max_retries:
            try:
                logger.info(f"📥 Baixando vídeo... tentativa {attempt + 1}/{max_retries}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                break  # Sucesso
            except yt_dlp.utils.DownloadError as e:
                err_msg = str(e)
                logger.error(f"Erro no download: {err_msg}")
                if "HTTP Error 429" in err_msg:
                    logger.warning(f"Erro 429 (Too Many Requests). Aguardando {sleep_seconds}s...")
                    time.sleep(sleep_seconds)
                    attempt += 1
                    if attempt == max_retries:
                        return {
                            "status": "error",
                            "message": f"Falha após {max_retries} tentativas (erro 429)."
                        }
                else:
                    return {"status": "error", "message": err_msg}
        else:
            return {"status": "error", "message": "Download falhou após múltiplas tentativas."}

        # Detectar arquivo baixado
        downloaded_files = glob.glob("input_video.*")
        if not downloaded_files:
            return {"status": "error", "message": "Arquivo de vídeo não encontrado após download."}
        input_path = downloaded_files[0]
        logger.info(f"📂 Arquivo baixado: {input_path}")

        output_path = "output_clip.mp4"

        # ==============================
        # 2. CORTAR VÍDEO COM FFMPEG
        # ==============================
        logger.info("✂️ Cortando vídeo...")
        try:
            subprocess.run([
                'ffmpeg',
                '-i', input_path,
                '-ss', start_time,
                '-t', duration,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro no ffmpeg: {e.stderr.decode()}")
            return {"status": "error", "message": "Erro no corte do vídeo."}

        # ==============================
        # 3. AUTENTICAÇÃO NA API YOUTUBE
        # ==============================
        logger.info("🔑 Autenticando no YouTube...")
        youtube = get_youtube_service()

        # ==============================
        # 4. UPLOAD PARA O YOUTUBE
        # ==============================
        logger.info("🚀 Enviando para o YouTube...")
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['Shorts', 'Automated', 'YouTube API'],
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'public',
                'madeForKids': False
            }
        }

        media = MediaFileUpload(output_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None

        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Progresso do upload: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"✅ Upload finalizado! Link: {video_link}")

        # ==============================
        # 5. LIMPEZA
        # ==============================
        try:
            os.remove(input_path)
            os.remove(output_path)
            logger.info("🧹 Arquivos temporários removidos.")
        except Exception as e:
            logger.warning(f"Não foi possível remover arquivos: {e}")

        return {"status": "success", "video_id": video_id, "video_link": video_link}

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {"status": "error", "message": f"Erro inesperado: {str(e)}"}