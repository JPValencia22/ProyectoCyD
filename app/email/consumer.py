import os
import aio_pika
import asyncio
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from email_sender import send_email  # Función de envío de correos ya implementada

# Configuración de MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["dsf_database"]
collection = db["security_keys"]

async def process_message(message):
    async with message.process():
        email_data = json.loads(message.body)
        try:
            print("Procesando mensaje...")
            load_dotenv()

            # Enviar el correo usando Mailtrap
            send_email(
                recipient=email_data["recipient"],
                subject=email_data["subject"],
                body=email_data["body"],
                smtp_server="smtp.gmail.com",  # Servidor SMTP de Mailtrap
                smtp_port=587,                  # Puerto de Mailtrap
                sender_email=os.getenv("AMAZON_USER"),  # Usuario de Mailtrap
                sender_password=os.getenv("AMAZON_PASSWORD")  # Contraseña de Mailtrap
            )

            # Guardar en MongoDB
            security_key = email_data.get("body").split("es:")[-1].strip().split()[0]
            collection.insert_one({
                "email": email_data["recipient"],
                "security_key": security_key
            })
            print(f"Correo enviado y clave guardada: {security_key}")

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

async def consume():
    try:
        connection = await aio_pika.connect_robust("amqp://localhost/")
        async with connection:
            channel = await connection.channel()

            # Declarar la cola
            queue = await channel.declare_queue("email_queue", durable=True)

            # Procesar mensajes concurrentemente
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    asyncio.create_task(process_message(message))

    except Exception as e:
        print(f"Error en el consumidor: {e}")
    finally:
        # Cierra la conexión de MongoDB
        mongo_client.close()
        print("Conexión a MongoDB cerrada.")

# Ejecutar el consumidor
if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Consumidor detenido manualmente.")
