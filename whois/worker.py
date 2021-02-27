import pika
from datetime import datetime
from whois.database import db, Device


connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()


result = channel.queue_declare(queue="whohacks", exclusive=False)
queue_name = result.method.queue

channel.queue_bind(exchange="whohacks", queue=queue_name, routing_key="")

print(" [*] Waiting for logs. To exit press CTRL+C")


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    Device.update_or_create(mac_address=body.decode(), last_seen=datetime.now())


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
