import logging
import socket

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


def kafka_client() -> Producer:
    hostname = socket.gethostname()
    servers = 'localhost:9092'
    logger.info(f"Connecting to Kafka server with the following information: {hostname} - {servers}")
    conf = {'bootstrap.servers': servers,
            'client.id': hostname}
    return Producer(conf)
