from django.core.mail import send_mail

send_mail(
    subject='Prueba de correo Geodepol',
    message='Este es un mensaje de prueba enviado desde el sistema Geodepol usando Gmail SMTP.',
    from_email='fiscalia.envios.geodepol@gmail.com',
    recipient_list=['tu_correo_personal@gmail.com'],  # cambia por tu correo real
    fail_silently=False,
)
