import os, subprocess, uuid

def process_video(video_url):
    uid = str(uuid.uuid4())
    output_dir = f"upload/{uid}"
    os.makedirs(output_dir, exist_ok=True)

    video_path = f"{output_dir}/video.mp4"
    subprocess.run(["yt-dlp", "-o", video_path, video_url])

    cut_path = f"{output_dir}/cut.mp4"
    subprocess.run(["ffmpeg", "-ss", "00:00:10", "-i", video_path, "-t", "60", "-c", "copy", cut_path])

    print(f"Vídeo cortado salvo em: {cut_path}")