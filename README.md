# DCI Kafka

DCI Kafka consumes events from Kafka and forwards them to DCI Feeder over HTTP.

## Reliability model

All service instances must use the same Kafka consumer group so each event is
processed by only one instance.

Kafka auto-commit is enabled. Invalid messages and events that still fail after
all HTTP attempts are logged and skipped. There is no DLQ or automatic replay.

HTTP retries can cause duplicate deliveries when a response is lost after the
Feeder accepted the request. Kafka rebalances can also cause the same event to
be processed by multiple instances. The receiving endpoint must therefore be
idempotent.

## Configuration

The following environment variables are required:

- `KAFKA_BOOTSTRAP_SERVERS`: comma-separated Kafka bootstrap servers
- `KAFKA_CONSUMER_TOPICS`: comma-separated topics to consume
- `DCI_FEEDER_URL`: complete DCI Feeder destination URL
- `KAFKA_SASL_USERNAME`: SASL username
- `KAFKA_SASL_PASSWORD`: SASL password

Optional variables:

- `KAFKA_CONSUMER_GROUP_ID` defaults to `DCI-FEEDER-CONSUMER`; use the same
  value on every instance
- `KAFKA_AUTO_OFFSET_RESET` defaults to `earliest`
- `KAFKA_SECURITY_PROTOCOL` defaults to `SASL_SSL`
- `KAFKA_SASL_MECHANISM` defaults to `SCRAM-SHA-512`
- `KAFKA_HTTP_MAX_ATTEMPTS` defaults to `3` and includes the initial request
- `KAFKA_HTTP_BACKOFF_SECONDS` defaults to `1`
- `KAFKA_MAX_POLL_INTERVAL_MS` defaults to `300000` and must exceed the maximum
  HTTP processing duration


## Run

```console
KAFKA_BOOTSTRAP_SERVERS=kafka.example.org:9093 \
KAFKA_CONSUMER_TOPICS=rhdl.events \
KAFKA_SASL_USERNAME=dci \
KAFKA_SASL_PASSWORD=secret \
DCI_FEEDER_URL=https://dci-feeder.example.org/events \
dci-kafka-consumer
```
