FROM registry.access.redhat.com/ubi8/ubi-minimal

LABEL name="DCI UMB" version="0.0.2"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"
ARG QUAY_EXPIRES_AFTER=never
LABEL quay.expires-after=${QUAY_EXPIRES_AFTER}

ENV LANG en_US.UTF-8

COPY . /opt/dci-umb

RUN microdnf -y upgrade && \
  microdnf install python3.11 python3.11-pip && \
  rpm -qa | sort > /tmp/rpms_before && \
  microdnf install python3.11-devel openssl-devel python3.11-wheel gcc findutils && \
  rpm -qa | sort > /tmp/rpms_after && \
  python3 -m pip install /opt/dci-umb && \
  comm -13 /tmp/rpms_before /tmp/rpms_after | xargs microdnf remove && \
  microdnf clean all && \
  rm -r /opt/dci-umb

COPY RH-IT-Root-CA.crt 2022-IT-Root-CA.pem /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust

CMD ["/usr/local/bin/dci-umb"]
