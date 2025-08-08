import os
import yt_dlp
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials

# Função principal que orquestra tudo
def process_video(youtube_url, start_time="00:00:00", duration="00:01:00", title="Short Video", description="Clipped from original"):
    try:
        # 1. Baixar o vídeo do YouTube
        print("Baixando vídeo...")
        ydl_opts = {
            'outtmpl': 'input_video.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        input_path = "input_video.mp4"
        output_path = "output_clip.mp4"

        # 2. Cortar o vídeo com ffmpeg
        print("Cortando vídeo...")
        subprocess.run([
            'ffmpeg',
            '-i', input_path,
            '-ss', start_time,
            '-t', duration,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # sobrescreve se já existir
            output_path
        ], check=True)

        # 3. Autenticação YouTube
        print("Autenticando no YouTube...")
        credentials = OAuth2Credentials(
            access_token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
            client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
            token_expiry=None,
            token_uri="https://oauth2.googleapis.com/token",
            user_agent=""
        )

        youtube = build('youtube', 'v3', credentials=credentials)

        # 4. Fazer upload para o YouTube
        print("Enviando para o YouTube...")
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['Shorts', 'Clips', 'Automated'],
                'categoryId': '22'  # People & Blogs
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
                print(f"Progresso: {int(status.progress() * 100)}%")

        print("Upload finalizado!")
        print("Vídeo publicado com ID:", response.get("id"))

        return {"status": "success", "video_id": response.get("id")}

    except Exception as e:
        print("Erro no processamento:", str(e))
        return {"status": "error", "message": str(e)}

    print(f"✂️ Vídeo cortado salvo em: {cut_path}")

    upload_to_youtube(cut_path, title="Shorts automático via IA")

