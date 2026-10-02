FROM registry.access.redhat.com/ubi10/ubi-minimal

LABEL name="DCI Kafka" version="0.1.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

COPY . /opt/dci-kafka

RUN microdnf -y upgrade && \
  microdnf -y install python3.12 python3.12-pip && \
  python3 -m pip install /opt/dci-kafka && \
  microdnf clean all && \
  rm -r /opt/dci-kafka

COPY RH-IT-Root-CA.crt 2022-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust

CMD ["/usr/local/bin/dci-kafka-consumer"]
