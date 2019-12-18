# DCI UMB

Start the sandbox server:

    python sandbox/server.py

In another terminal start dci-umb with parameters

    PYTHONPATH=. python dci_umb/main.py \
        --key ./prod.key \
        --crt ./prod.crt \
        --ca ./RH-IT-Root-CA.crt \
        --broker amqps://messaging-devops-broker02.web.prod.ext.phx2.redhat.com:5671 \
        --source "topic://VirtualTopic.eng.brew.task.*" \
        --destination "http://localhost:5000/api/v1/events"

## Production run

    PYTHONPATH=. python dci_umb/main.py \
        --key ./prod.key \
        --crt ./prod.crt \
        --ca ./RH-IT-Root-CA.crt \
        --broker amqps://messaging-devops-broker02.web.prod.ext.phx2.redhat.com:5671 \
        --source "topic://VirtualTopic.eng.rtt.ci" \
        --destination "https://feeder.distributed-ci.io/api/v1/events"

## Example of events

```json
{
  "i": 0,
  "msg_id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-39557-1571864839674-5:25646:0:0:1",
  "topic": "/topic/VirtualTopic.eng.rtt.ci",
  "timestamp": 1571903692.0,
  "certificate": null,
  "signature": null,
  "username": null,
  "crypto": null,
  "msg": {
    "arches": [
      "aarch64",
      "x86_64",
      "s390x",
      "ppc64le"
    ],
    "bkr_info": {
      "distro_id": 11256,
      "distro_name": "RHEL-8.2.0-20191024.n.0",
      "distro_tags": [
        "RTT_PASSED",
        "RTT_PASSED_PRIMARY"
      ],
      "distro_version": "RedHatEnterpriseLinux8.2"
    },
    "build": "RHEL-8.2.0-20191024.n.0",
    "build_url": "http://download.eng.bos.redhat.com//rhel-8/nightly/RHEL-8/RHEL-8.2.0-20191024.n.0/",
    "product": "RHEL",
    "version": "8.2.0"
  },
  "headers": {
    "BUILD": "RHEL-8.2.0-20191024.n.0",
    "CI_NAME": "rtt-beaker-acceptance-tests-done",
    "CI_TYPE": "tier-1-testing-done",
    "JMSXUserID": "msg-client-rtt",
    "JMS_AMQP_MESSAGE_FORMAT": "0",
    "JMS_AMQP_NATIVE": "false",
    "PRODUCT": "RHEL",
    "PUBLISHER": "RTT",
    "RTT_PASSED": "true",
    "RTT_PASSED_PRIMARY": "true",
    "TYPE": "nightly",
    "VERSION": "8.2.0",
    "amq6100_destination": "queue://Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "amq6100_originalDestination": "topic://VirtualTopic.eng.rtt.ci",
    "correlation-id": "064ef94f-c4ed-4d4e-9b1d-ac767d578877",
    "destination": "/topic/VirtualTopic.eng.rtt.ci",
    "expires": "0",
    "message-id": "ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-39557-1571864839674-5:25646:0:0:1",
    "original-destination": "/topic/VirtualTopic.eng.rtt.ci",
    "priority": "4",
    "subscription": "/queue/Consumer.client-datanommer.upshift-prod.VirtualTopic.eng.>",
    "timestamp": "0",
    "type": "application/json"
  },
  "source_name": "datanommer",
  "source_version": "0.9.1"
}
```

[rel eng event](https://datagrepper.engineering.redhat.com/id?id=ID:messaging-devops-broker01.web.prod.ext.phx2.redhat.com-41882-1571157850402-3:268902:0:0:1&is_raw=true&size=extra-large)

[nigthly event](https://datagrepper.engineering.redhat.com/id?id=ID:messaging-devops-broker02.web.prod.ext.phx2.redhat.com-39557-1571864839674-5:25646:0:0:1&is_raw=true&size=extra-large)