import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit("Defina CLIENT_ID e CLIENT_SECRET no ambiente (export CLIENT_ID=... CLIENT_SECRET=...).")

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [
                "http://localhost:8080/oauth2callback",
                "http://localhost:5000/oauth2callback",
                "https://post-youtube.onrender.com/oauth2callback",
                "https://videoprocessor.contannarv14.repl.co/oauth2callback"
            ],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=[
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube"
    ]
)

auth_url, _ = flow.authorization_url(
    prompt='consent',
    access_type='offline',
    include_granted_scopes='true'
)

print("\nAbra este link no navegador, autorize e copie o CÓDIGO mostrado:\n")
print(auth_url)
print("\nDepois rode:  python generate_oauth_tokens.py \"COLOQUE_O_CODIGO_AQUI\"\n")
