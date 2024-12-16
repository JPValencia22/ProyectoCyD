import random
import string
import pika
import json

def generate_random_password(length=10):
    """
    Genera una contraseña aleatoria de la longitud especificada.
    Contiene letras mayúsculas, minúsculas, números y caracteres especiales.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def publish_email_message(queue, message_body):
    # Conectar al servidor RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Declarar la cola con `durable=True` para que coincida con el consumidor
    channel.queue_declare(queue=queue, durable=True)

    # Publicar el mensaje
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message_body),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Hace que el mensaje sea persistente
        ),
    )
    print(f"Mensaje enviado a la cola '{queue}': {message_body}")

    # Cerrar la conexión
    connection.close()

# Generar contraseña aleatoria
random_password = generate_random_password()

# Datos del mensaje
email_data = {
    "recipient": "juanpablovalenciachaves@gmail.com",  # Cambia esto por un destinatario válido de prueba
    "subject": "Contraseña de acceso al sistema",
    "body": f"Hola, gracias por preferirnos.\n\nTu contraseña de acceso al sistema es: {random_password}\n\nTus desarrolladores de confianza,\nVanessa y Juan Pablo"
}

# Publicar el mensaje
publish_email_message("email_queue", email_data)
