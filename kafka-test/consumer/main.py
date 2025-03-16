import json
import os
import time
from kafka import KafkaConsumer
import mysql.connector

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kraft-cluster-kafka-bootstrap.kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "my-topic")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "testdb")

# enable_auto_commit를 False로 설정
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username="jslee",
    sasl_plain_password="U3Myy7CdLk6YCZh6XDEtParQ9I5yn81m",
    auto_offset_reset='earliest',
    enable_auto_commit=False,  # 수동 커밋 사용
    group_id='consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# MySQL 연결
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
cursor = db.cursor()

batch = []
commit_interval = 1  # 1초마다 커밋
last_commit_time = time.time()

sql = """
INSERT INTO credentials (id, password)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE password = VALUES(password)
"""

print("Consumer started. Waiting for messages...")

try:
    while True:
        records = consumer.poll(timeout_ms=1000)
        for topic_partition, messages in records.items():
            for message in messages:
                data = message.value
                # 데이터 형식 검증 추가
                if "id" in data and "password" in data:
                    batch.append((data['id'], data['password']))
                else:
                    print("Invalid message format:", data)

        current_time = time.time()
        if current_time - last_commit_time >= commit_interval:
            if batch:
                try:
                    cursor.executemany(sql, batch)
                    db.commit()
                    consumer.commit()
                    print(f"Inserted batch of {len(batch)} records.")
                except Exception as e:
                    db.rollback()
                    print("Error inserting batch data:", e)
                batch.clear()
            last_commit_time = current_time
except KeyboardInterrupt:
    print("Shutting down gracefully...")
finally:
    consumer.close()
    cursor.close()
    db.close()
