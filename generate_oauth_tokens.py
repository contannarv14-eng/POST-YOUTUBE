import os, sys, json, time
from google_auth_oauthlib.flow import InstalledAppFlow

if len(sys.argv) < 2:
    print("Uso: python generate_oauth_tokens.py \"CODIGO_COLADO_DO_GOOGLE\"")
    raise SystemExit(1)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit("Defina CLIENT_ID e CLIENT_SECRET no ambiente (export CLIENT_ID=... CLIENT_SECRET=...).")

auth_code = sys.argv[1]

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

# Troca o código pelos tokens
flow.fetch_token(code=auth_code)
creds = flow.credentials

payload = {
    "access_token": creds.token,
    "refresh_token": getattr(creds, "refresh_token", None),
    "token_uri": creds.token_uri,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scopes": list(creds.scopes or []),
    "expiry": creds.expiry.isoformat() if getattr(creds, "expiry", None) else None,
}

# Salva localmente (IGNORADO pelo git via .gitignore)
with open("tokens.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

# Gera um arquivo de conveniência para export no shell (não versionado)
with open("tokens.env", "w", encoding="utf-8") as f:
    f.write(f'ACCESS_TOKEN="{payload["access_token"]}"\n')
    if payload["refresh_token"]:
        f.write(f'REFRESH_TOKEN="{payload["refresh_token"]}"\n')

print("\n✅ Tokens gerados com sucesso.")
print("→ Arquivo salvo: tokens.json (não é versionado)")
print("→ Conveniência: tokens.env (use `source tokens.env` no Git Bash)")
if not payload.get("refresh_token"):
    print("⚠️ O Google não retornou refresh_token. Rode o fluxo novamente usando prompt=consent, access_type=offline, e apague tokens anteriores antes de tentar.")
