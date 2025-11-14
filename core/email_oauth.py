import base64
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


# ================================
# CONFIGURACIÓN OAUTH – GMAIL
# *** Cambia estos valores luego del deploy ***
# ================================
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
EMAIL = os.getenv("GOOGLE_OAUTH_EMAIL")




# ================================
# 1. Generar TOKEN OAUTH2
# ================================
def generate_oauth2_token():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    creds.refresh(Request())
    access_token = creds.token

    auth_string = f"user={EMAIL}\1auth=Bearer {access_token}\1\1"
    return base64.b64encode(auth_string.encode()).decode()


# ================================
# 2. Enviar correo usando SMTP con OAUTH2
# ================================
def enviar_correo_oauth(destinatario, asunto, mensaje_html, ruta_adjunto=None):
    auth_token = generate_oauth2_token()

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = EMAIL
    msg["To"] = destinatario

    # Contenido HTML
    msg.attach(MIMEText(mensaje_html, "html"))

    # Adjunto opcional
    if ruta_adjunto:
        try:
            with open(ruta_adjunto, "rb") as f:
                adj = MIMEApplication(f.read(), _subtype="pdf")
                adj.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=ruta_adjunto.split("/")[-1]
                )
                msg.attach(adj)
        except Exception as e:
            raise Exception(f"Error al adjuntar archivo PDF: {e}")

    # Conectar a Gmail SMTP con OAuth2
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.docmd("AUTH", "XOAUTH2 " + auth_token)

        server.sendmail(EMAIL, [destinatario], msg.as_string())
        server.quit()

    except Exception as e:
        raise Exception(f"Error al enviar correo mediante OAuth2: {e}")

