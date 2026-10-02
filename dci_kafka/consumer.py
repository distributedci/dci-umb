import json
import logging
import math
import os
import signal
import time

import requests
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)
shutdown_requested = False


def signal_handler(signum, _frame):
    global shutdown_requested
    logger.info("Received signal %s, initiating graceful shutdown", signum)
    shutdown_requested = True


def get_kafka_config():
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "")
    if not bootstrap_servers:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    topics = os.environ.get("KAFKA_CONSUMER_TOPICS", "")
    if not topics:
        raise ValueError("KAFKA_CONSUMER_TOPICS environment variable is required")

    dci_feeder_url = os.environ.get("DCI_FEEDER_URL", "")
    if not dci_feeder_url:
        raise ValueError("DCI_FEEDER_URL environment variable is required")

    return {
        "bootstrap_servers": [
            server.strip() for server in bootstrap_servers.split(",")
        ],
        "topics": [topic.strip() for topic in topics.split(",")],
        "auto_offset_reset": os.environ.get("KAFKA_AUTO_OFFSET_RESET", "earliest"),
        "security_protocol": os.environ.get("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
        "group_id": os.environ.get("KAFKA_CONSUMER_GROUP_ID", "DCI-FEEDER-CONSUMER"),
        "sasl_mechanism": os.environ.get("KAFKA_SASL_MECHANISM", "SCRAM-SHA-512"),
        "sasl_plain_username": os.environ.get("KAFKA_SASL_USERNAME"),
        "sasl_plain_password": os.environ.get("KAFKA_SASL_PASSWORD"),
        "dci_feeder_url": dci_feeder_url,
        "http_max_attempts": int(os.environ.get("KAFKA_HTTP_MAX_ATTEMPTS", "3")),
        "http_backoff_seconds": float(
            os.environ.get("KAFKA_HTTP_BACKOFF_SECONDS", "1")
        ),
        "max_poll_interval_ms": int(
            os.environ.get("KAFKA_MAX_POLL_INTERVAL_MS", "300000")
        ),
    }


def validate_kafka_config(config):
    if (
        not math.isfinite(config["http_max_attempts"])
        or config["http_max_attempts"] <= 0
    ):
        raise ValueError("KAFKA_HTTP_MAX_ATTEMPTS must be finite and strictly positive")
    if (
        not math.isfinite(config["http_backoff_seconds"])
        or config["http_backoff_seconds"] < 0
    ):
        raise ValueError("KAFKA_HTTP_BACKOFF_SECONDS must be finite and non-negative")


def kafka_client_config(config):
    return {
        "bootstrap_servers": config["bootstrap_servers"],
        "security_protocol": config["security_protocol"],
        "sasl_mechanism": config["sasl_mechanism"],
        "sasl_plain_username": config["sasl_plain_username"],
        "sasl_plain_password": config["sasl_plain_password"],
        "max_poll_interval_ms": config["max_poll_interval_ms"],
    }


def build_consumer(config):
    return KafkaConsumer(
        *config["topics"],
        group_id=config["group_id"],
        auto_offset_reset=config["auto_offset_reset"],
        enable_auto_commit=True,
        **kafka_client_config(config),
    )


def post_event(value_json, dci_feeder_url, session):
    response = session.post(
        dci_feeder_url,
        json=value_json,
        timeout=(10, 30),
    )
    response.raise_for_status()
    return response


def post_event_with_retry(value_json, config, session):
    max_attempts = config["http_max_attempts"]

    for attempt in range(1, max_attempts + 1):
        try:
            response = post_event(value_json, config["dci_feeder_url"], session)
            logger.info(
                "Successfully posted event to %s - Status: %s",
                config["dci_feeder_url"],
                response.status_code,
            )
            return response
        except requests.exceptions.RequestException as error:
            if shutdown_requested or attempt == max_attempts:
                raise
            delay = config["http_backoff_seconds"] * (2**attempt)
            logger.warning(
                "Failed to post event to DCI Feeder: %s; retrying in %s seconds",
                error,
                delay,
            )
            time.sleep(delay)


def poll_messages(consumer):
    while not shutdown_requested:
        records = consumer.poll(timeout_ms=1000, max_records=1)
        for messages in records.values():
            if shutdown_requested:
                return
            yield from messages


def process_message(message, config, session):
    logger.info(
        "Topic: %s | Partition: %s | Offset: %s | Key: %s",
        message.topic,
        message.partition,
        message.offset,
        message.key.decode("utf-8", errors="replace") if message.key else None,
    )

    try:
        if message.value is None:
            raise TypeError("Kafka tombstone has no value")
        value_json = json.loads(message.value)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as error:
        logger.error("Invalid JSON message: %s", error)
        return

    try:
        post_event_with_retry(value_json, config, session)
    except requests.exceptions.RequestException as error:
        logger.error(
            "Failed to process event at %s:%s:%s after attempts: %s",
            message.topic,
            message.partition,
            message.offset,
            error,
        )


def consume_messages(consumer, config, session):
    message_count = 0
    try:
        for message in poll_messages(consumer):
            message_count += 1
            process_message(message, config, session)
    finally:
        consumer.close(autocommit=False)
        logger.info("Consumer closed. Total messages processed: %s", message_count)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("kafka").setLevel(logging.INFO)

    try:
        config = get_kafka_config()
        validate_kafka_config(config)
        logger.info("Starting Kafka consumer with configuration:")
        logger.info("  Bootstrap servers: %s", config["bootstrap_servers"])
        logger.info("  Topics: %s", config["topics"])
        logger.info("  Group Id: %s", config["group_id"])
        logger.info("  Auto offset reset: %s", config["auto_offset_reset"])
        logger.info("  SASL mechanism: %s", config["sasl_mechanism"])
        logger.info("  Security protocol: %s", config["security_protocol"])

        consumer = build_consumer(config)

        logger.info("Successfully connected to Kafka")
        logger.info("DCI Feeder URL: %s", config["dci_feeder_url"])
        with requests.Session() as session:
            consume_messages(consumer, config, session)
        return 0
    except (ValueError, KafkaError):
        logger.exception("Kafka consumer error")
        return 1
    except Exception:
        logger.exception("Fatal error")
        return 1
