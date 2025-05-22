import json

import pika


class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq", port=5672, heartbeat=30, blocked_connection_timeout=60)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="email_queue", durable=True)

    def close(self):
        if self.connection:
            self.connection.close()

    async def send_email_task(self, email_data: dict):
        if not self.channel:
            raise RuntimeError("RabbitMQ channel is not initialized.")
        self.channel.basic_publish(
            exchange="", routing_key="email_queue", body=json.dumps(email_data)
        )


rabbitmq = RabbitMQConnection()
