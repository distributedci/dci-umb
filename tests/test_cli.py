from pytest import raises
from dci_umb.cli import parse_arguments


def test_parse_arguments():
    args = parse_arguments(
        [
            "--key",
            "/tmp/prod.key",
            "--crt",
            "/tmp/prod.crt",
            "--ca",
            "/tmp/RH-IT-Root-CA.crt",
            "--broker",
            "amqps://broker01.redhat.com:5671",
            "--broker",
            "amqps://broker02.redhat.com:5671",
            "--source",
            "topic://VirtualTopic.*>",
            "--destination",
            "http://localhost:5000/api/v1/events",
        ]
    )
    assert args["key_file"] == "/tmp/prod.key"
    assert args["crt_file"] == "/tmp/prod.crt"
    assert args["ca_file"] == "/tmp/RH-IT-Root-CA.crt"
    assert args["brokers"] == [
        "amqps://broker01.redhat.com:5671",
        "amqps://broker02.redhat.com:5671",
    ]
    assert args["source"] == "topic://VirtualTopic.*>"
    assert args["destination"] == "http://localhost:5000/api/v1/events"
