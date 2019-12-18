# Copyright 2019 Red Hat
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging

from proton import SSLDomain
from proton.handlers import MessagingHandler
from dci_umb.bus import Bus
from dci_umb.handler import HTTPBouncerMessageHandler


logger = logging.getLogger(__name__)


class Receiver(MessagingHandler):
    def __init__(self, settings):
        super(Receiver, self).__init__()
        handlers = [HTTPBouncerMessageHandler(destination=settings.get("destination"))]
        self.bus = Bus(handlers=handlers)
        self.settings = settings

    def on_start(self, event):
        logger.debug("UMB receiver on_start")
        domain = SSLDomain(SSLDomain.MODE_CLIENT)
        crt_file = self.settings.get("crt_file")
        key_file = self.settings.get("key_file")
        ca_file = self.settings.get("ca_file")
        domain.set_credentials(crt_file, key_file, None)
        domain.set_trusted_ca_db(ca_file)
        domain.set_peer_authentication(SSLDomain.VERIFY_PEER)
        brokers = self.settings.get("brokers")
        conn = event.container.connect(urls=brokers, ssl_domain=domain)
        source = self.settings.get("source")
        event.container.create_receiver(conn, source=source)

    def on_message(self, event):
        self.bus.dispatch_event(event)

    def on_link_opened(self, event):
        logger.debug("on_link_opened")
        logger.debug("event.connection.hostname: %s" % event.connection.hostname)
        logger.debug(
            "event.receiver.source.address: %s" % event.receiver.source.address
        )

    def on_link_error(self, event):
        logger.debug("on_link_error")
        logger.debug("link error: %s" % event.link.remote_condition.name)
        logger.debug(event.link.remote_condition.description)
        logger.debug("closing connection to: %s" % event.connection.hostname)
        event.connection.close()

    def on_transport_error(self, event):
        logger.debug("on_transport_error")
        logger.debug(event)
        condition = event.transport.condition
        if condition:
            logger.debug(
                "transport error: %s: %s" % (condition.name, condition.description)
            )
            if condition.name in self.fatal_conditions:
                logger.debug("fatal error, close connection")
                event.connection.close()
        else:
            logger.debug("unspecified transport error")
