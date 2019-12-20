# -*- coding: utf-8 -*-
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
import argparse

import requests


def get_event(url):
    return requests.get(url).json()


def replay_event(event):
    return requests.post("http://feeder.distributed-ci.io/events", json=event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay an event")
    parser.add_argument(
        "url", help="Replay events from datagrepper on feeder.distributed-ci.io"
    )
    args = vars(parser.parse_args())
    event = get_event(args["url"])
    response = replay_event(event)
    status_code = response.status_code
    response_body = response.json()
    if status_code == 201:
        print(response_body)
    else:
        print("Error: %s" % response_body)
