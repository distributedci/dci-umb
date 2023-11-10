FROM registry.access.redhat.com/ubi8/ubi-minimal

LABEL name="DCI UMB" version="0.0.1"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

COPY . /opt/dci-umb
COPY ../dci-packaging /opt/dci-packaging

RUN microdnf -y install python3.11 python3.11-pip && \
    rpm -qa | sort > /tmp/rpms_before && \
    microdnf install python3.11-devel openssl-devel python3.11-wheel gcc findutils && \
    rpm -qa | sort > /tmp/rpms_after && \
    PYTHONPATH=../dci-packaging python3 -m pip install /opt/dci-umb && \
    comm -13 /tmp/rpms_before /tmp/rpms_after | xargs microdnf remove && \
    microdnf clean all && \
    rm -r /opt/dci-umb

COPY RH-IT-Root-CA.crt /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt
RUN update-ca-trust

CMD ["/usr/local/bin/dci-umb"]
