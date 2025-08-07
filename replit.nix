{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    pkgs.yt-dlp
    pkgs.python3
    pkgs.python3Packages.flask
  ];
}