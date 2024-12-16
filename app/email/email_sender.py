import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException, SMTPAuthenticationError, SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError

def send_email(recipient, subject, body, smtp_server, smtp_port, sender_email, sender_password):
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = "Equipo de Soporte"
        msg["To"] = recipient
        msg["Subject"] = subject

        # Asegurarse de que el cuerpo del correo esté en UTF-8
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Conectarse al servidor SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Inicia TLS
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())

            print(f"Correo enviado a {recipient}.")
    except SMTPAuthenticationError:
        print("Error de autenticación: Verifica tu usuario y contraseña.")
    except SMTPRecipientsRefused:
        print("Error: Todos los destinatarios fueron rechazados.")
    except SMTPSenderRefused:
        print("Error: El remitente fue rechazado.")
    except SMTPDataError:
        print("Error: El servidor respondió con un código de error inesperado.")
    except SMTPException as e:
        print(f"Error al enviar correo: {e}")
