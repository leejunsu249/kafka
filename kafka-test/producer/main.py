import os
import json
import random
import string
from fastapi import FastAPI
from kafka import KafkaProducer

app = FastAPI()

# Kafka 브로커 주소는 환경변수로 설정(기본값은 "kafka:9092")
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_PLAINTEXT",  
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username="jslee",  
    sasl_plain_password="U3Myy7CdLk6YCZh6XDEtParQ9I5yn81m", 
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    enable_idempotence=True,
    retries=3    
)

def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.get("/produce")
def produce_message():
    message = {
        "id": random_string(8),
        "password": random_string(12)
    }
    producer.send("my-topic", value=message)
    producer.flush()  # 메시지가 바로 전송되도록 flush
    return {"status": "message sent", "message": message}
