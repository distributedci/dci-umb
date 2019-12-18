#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse


EXAMPLES = """
examples:
  # listen on virtual topic "topic://VirtualTopic.dci.*>"
  # and bounce all the events to an http endpoint "http://localhost:5000/api/v1/events"
  dci-umb --key /tmp/prod.key --crt /tmp/prod.crt --ca /tmp/RH-IT-Root-CA.crt --source "topic://VirtualTopic.dci.*>" --destination "http://localhost:5000/api/v1/events"
"""

COPYRIGHT = """
copyright:
  Copyright © 2019 Red Hat.
  Licensed under the Apache License, Version 2.0
"""


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(
        usage="dci-umb [OPTIONS]",
        description=" listen on virtual topic and bounce all the events",
        epilog=EXAMPLES + COPYRIGHT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--key",
        dest="key_file",
        metavar="KEY_FILE_PATH",
        help="key file to identify the connection to UMB",
    )
    parser.add_argument(
        "--crt",
        dest="crt_file",
        metavar="CRT_FILE_PATH",
        help="cert file to identify the connection to UMB",
    )
    parser.add_argument(
        "--ca",
        dest="ca_file",
        metavar="CA_FILE_PATH",
        help="ca file to identify the connection to UMB",
    )
    parser.add_argument(
        "--broker",
        action="append",
        metavar="BROKER",
        dest="brokers",
        default=[],
        help="amqps broker to listen to",
    )
    parser.add_argument(
        "--source",
        dest="source",
        metavar="SOURCE",
        help="virtual topic source to listen to",
    )
    parser.add_argument(
        "--destination",
        dest="destination",
        metavar="DESTINATION",
        help="destination for the bounced events",
    )
    parsed_arguments = parser.parse_args(arguments)
    return vars(parsed_arguments)
