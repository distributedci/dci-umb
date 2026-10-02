from unittest import mock

import pytest
import requests

from dci_kafka import consumer


@pytest.fixture
def config():
    return {
        "bootstrap_servers": ["kafka.example.org:9093"],
        "topics": ["rhdl.events"],
        "auto_offset_reset": "earliest",
        "security_protocol": "SASL_SSL",
        "group_id": "DCI-FEEDER-CONSUMER",
        "sasl_mechanism": "SCRAM-SHA-512",
        "sasl_plain_username": "dci",
        "sasl_plain_password": "secret",
        "dci_feeder_url": "https://dci-feeder.example.org/events",
        "http_max_attempts": 3,
        "http_backoff_seconds": 0,
        "max_poll_interval_ms": 300000,
    }


@pytest.fixture
def session():
    return mock.Mock()


@pytest.fixture(autouse=True)
def reset_shutdown_requested():
    consumer.shutdown_requested = False
    yield
    consumer.shutdown_requested = False


def kafka_message(value=b'{"event": "created"}'):
    return mock.Mock(
        topic="rhdl.events",
        partition=2,
        offset=10,
        key=b"event-key",
        value=value,
        headers=[],
    )


def test_get_kafka_config_defaults(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-1:9093,kafka-2:9093")
    monkeypatch.setenv("KAFKA_CONSUMER_TOPICS", "rhdl.events,dci.events")
    monkeypatch.setenv("DCI_FEEDER_URL", "https://dci-feeder.example.org/events")

    config = consumer.get_kafka_config()

    assert config["bootstrap_servers"] == ["kafka-1:9093", "kafka-2:9093"]
    assert config["topics"] == ["rhdl.events", "dci.events"]
    assert config["group_id"] == "DCI-FEEDER-CONSUMER"
    assert config["dci_feeder_url"] == "https://dci-feeder.example.org/events"
    assert config["http_max_attempts"] == 3
    assert config["max_poll_interval_ms"] == 300000


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("http_max_attempts", 0),
        ("http_max_attempts", -1),
        ("http_backoff_seconds", -1),
        ("http_backoff_seconds", float("inf")),
    ],
)
def test_validate_kafka_config_rejects_invalid_values(config, key, value):
    config[key] = value

    with pytest.raises(ValueError):
        consumer.validate_kafka_config(config)


def test_build_consumer_always_enables_auto_commit(config, monkeypatch):
    kafka_consumer = mock.Mock()
    constructor = mock.Mock(return_value=kafka_consumer)
    monkeypatch.setattr(consumer, "KafkaConsumer", constructor)

    assert consumer.build_consumer(config) is kafka_consumer
    assert constructor.call_args.kwargs["enable_auto_commit"] is True


def test_consume_posts_successful_message(config, session, monkeypatch):
    message = kafka_message()
    kafka_consumer = mock.Mock()
    monkeypatch.setattr(consumer, "poll_messages", mock.Mock(return_value=[message]))
    monkeypatch.setattr(consumer, "post_event_with_retry", mock.Mock())

    consumer.consume_messages(kafka_consumer, config, session)

    consumer.post_event_with_retry.assert_called_once_with(
        {"event": "created"}, config, session
    )
    kafka_consumer.commit.assert_not_called()
    kafka_consumer.close.assert_called_once_with(autocommit=False)


def test_http_retries_with_exponential_backoff(config, session, monkeypatch):
    error = requests.exceptions.ConnectionError("unavailable")
    post_event = mock.Mock(side_effect=error)
    sleep = mock.Mock()
    monkeypatch.setattr(consumer, "post_event", post_event)
    monkeypatch.setattr(consumer.time, "sleep", sleep)

    with pytest.raises(requests.exceptions.ConnectionError) as raised:
        consumer.post_event_with_retry({}, config, session)

    assert raised.value is error
    assert post_event.call_count == 3
    assert sleep.call_args_list == [mock.call(0), mock.call(0)]


def test_post_event_with_retry_returns_response(config, session, monkeypatch):
    response = mock.Mock(status_code=200)
    post_event = mock.Mock(return_value=response)
    monkeypatch.setattr(consumer, "post_event", post_event)

    assert consumer.post_event_with_retry({}, config, session) is response
    post_event.assert_called_once_with({}, config["dci_feeder_url"], session)


def test_poll_messages_stops_after_shutdown_signal():
    kafka_consumer = mock.Mock()

    def poll(**kwargs):
        consumer.signal_handler(15, None)
        return {}

    kafka_consumer.poll.side_effect = poll

    assert list(consumer.poll_messages(kafka_consumer)) == []
    kafka_consumer.poll.assert_called_once_with(timeout_ms=1000, max_records=1)


def test_failed_post_is_logged_without_manual_offset_handling(
    config, session, monkeypatch, caplog
):
    message = kafka_message()
    kafka_consumer = mock.Mock()
    monkeypatch.setattr(consumer, "poll_messages", mock.Mock(return_value=[message]))
    error = requests.exceptions.HTTPError("bad gateway")
    monkeypatch.setattr(consumer, "post_event_with_retry", mock.Mock(side_effect=error))

    consumer.consume_messages(kafka_consumer, config, session)

    assert "Failed to process event" in caplog.text
    kafka_consumer.commit.assert_not_called()
    kafka_consumer.seek.assert_not_called()


def test_invalid_json_is_logged_without_manual_offset_handling(
    config, session, monkeypatch, caplog
):
    message = kafka_message(b"not-json")
    kafka_consumer = mock.Mock()
    monkeypatch.setattr(consumer, "poll_messages", mock.Mock(return_value=[message]))
    post = mock.Mock()
    monkeypatch.setattr(consumer, "post_event_with_retry", post)

    consumer.consume_messages(kafka_consumer, config, session)

    post.assert_not_called()
    assert "Invalid JSON message" in caplog.text
    kafka_consumer.commit.assert_not_called()
    kafka_consumer.seek.assert_not_called()
