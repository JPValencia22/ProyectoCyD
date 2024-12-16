import os
from app.email.email_sender import send_email

def test_send_email():
    recipient = "vanessaosorio252@gmail.com"
    subject = "Prueba de envío de correo"
    body = "Este es un correo de prueba."
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("AMAZON_USER")
    sender_password = os.getenv("AMAZON_PASSWORD")

    send_email(recipient, subject, body, smtp_server, smtp_port, sender_email, sender_password)

if __name__ == "__main__":
    test_send_email()
