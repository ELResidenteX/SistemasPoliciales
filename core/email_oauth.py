import base64
import os
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ===============================
# VARIABLES DESDE .env
# ===============================
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
EMAIL = os.getenv("GOOGLE_EMAIL_SENDER")

# ===============================
# 1. Obtener token de acceso
# ===============================
def obtener_access_token():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    creds.refresh(Request())
    return creds.token

# ===============================
# 2. Enviar correo usando Gmail API
# ===============================
def enviar_correo_oauth(destinatario, asunto, mensaje_html, ruta_adjunto=None):
    # Crear el correo MIME
    message = MIMEMultipart()
    message["To"] = destinatario
    message["From"] = EMAIL
    message["Subject"] = asunto

    # Cuerpo HTML
    message.attach(MIMEText(mensaje_html, "html"))

    # Adjuntar PDF si existe
    if ruta_adjunto:
        with open(ruta_adjunto, "rb") as f:
            adj = MIMEApplication(f.read(), _subtype="pdf")
            adj.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(ruta_adjunto)
            )
            message.attach(adj)

    # Codificar mensaje completo a base64 "URL-safe"
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Construir payload para Gmail API
    payload = {
        "raw": raw_message
    }

    # Token de acceso válido
    access_token = obtener_access_token()

    # Llamada HTTPS a Gmail API
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code not in [200, 202]:
        raise Exception(f"Error Gmail API: {response.status_code} - {response.text}")

    return True


