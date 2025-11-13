import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

API_KEY = "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"  # <- PÉGALA COMPLETA AQUÍ

message = Mail(
    from_email="geodepolplataform@gmail.com",
    to_emails="geodepolplataform@gmail.com",
    subject="Test API SendGrid",
    plain_text_content="Probando integración con SendGrid API Web"
)

try:
    sg = SendGridAPIClient(API_KEY)
    response = sg.send(message)
    print("STATUS:", response.status_code)
    print(response.body)
except Exception as e:
    print("ERROR:", e)

