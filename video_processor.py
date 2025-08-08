import os
import subprocess
import uuid
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials


def upload_to_youtube(video_path, title="Shorts Automático"):
    credentials = OAuth2Credentials(
        access_token=None,
        client_id=os.environ.get("YOUTUBE_CLIENT_ID"),
        client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET"),
        refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        token_expiry=None,
        token_uri='https://oauth2.googleapis.com/token',
        user_agent=''
    )

    youtube = build('youtube', 'v3', credentials=credentials)

    body = dict(
        snippet=dict(
            title=title,
            description="Corte automático de vídeo viral",
            tags=["shorts", "viral", "automação"],
            categoryId="24"  # Categoria: Entretenimento
        ),
        status=dict(
            privacyStatus="public"  # ou "unlisted", "private"
        )
    )

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📤 Enviando: {int(status.progress() * 100)}%")

    print("✅ Vídeo publicado com sucesso! ID:", response['id'])


def process_video(video_url):
    uid = str(uuid.uuid4())
    output_dir = f"upload/{uid}"
    os.makedirs(output_dir, exist_ok=True)

    video_path = f"{output_dir}/video.mp4"
    subprocess.run(["yt-dlp", "-o", video_path, video_url])

    cut_path = f"{output_dir}/cut.mp4"
    subprocess.run([
        "ffmpeg", "-ss", "00:00:10", "-i", video_path,
        "-t", "60", "-c", "copy", cut_path
    ])

    print(f"✂️ Vídeo cortado salvo em: {cut_path}")

    upload_to_youtube(cut_path, title="Shorts automático via IA")
