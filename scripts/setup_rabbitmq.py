import pika

def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la Dead Letter Queue
    channel.queue_declare(queue="dead_letter_queue", durable=True)

    # Declarar la cola principal con DLQ configurada
    channel.queue_declare(
        queue="email_queue",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",  # Usamos el exchange predeterminado
            "x-dead-letter-routing-key": "dead_letter_queue"  # Ruta hacia la DLQ
        }
    )

    print("Colas configuradas:")
    print("- email_queue (con Dead Letter Queue configurada)")
    print("- dead_letter_queue")
    
    # Declarar la cola de reintentos
    channel.queue_declare(
        queue="retry_queue",
        durable=True,
        arguments={
            "x-message-ttl": 60000,  # 60 segundos de espera
            "x-dead-letter-exchange": "",  # Redirigir mensajes expirados
            "x-dead-letter-routing-key": "email_queue"
        }
    )

    connection.close()

# Ejecutar la configuración
if __name__ == "__main__":
    setup_rabbitmq()

