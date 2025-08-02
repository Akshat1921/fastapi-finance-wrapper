from confluent_kafka import Producer
import json
import os

# Use environment variable with fallback
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'fastapi-stock-producer'
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed for {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def send_updated_stock_to_kafka(topic: str, data):
    try:
        # Convert data to JSON string if it's not already
        if isinstance(data, dict):
            message = json.dumps(data)
        elif isinstance(data, str):
            message = data
        else:
            message = json.dumps(data)
        
        producer.produce(
            topic=topic,
            value=message,
            callback=delivery_report
        )
        producer.poll(0)  # Trigger delivery report callbacks
        
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")
    finally:
        producer.flush()  # Ensure all messages are sent