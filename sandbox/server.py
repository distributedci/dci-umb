#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import uuid

from flask import Flask
from flask import request
from flask import jsonify


app = Flask(__name__)


@app.route("/api/v1/events", methods=["POST"])
def get_event():
    print(request.data.decode("utf-8"))
    return jsonify({"id": uuid.uuid4()})


if __name__ == "__main__":
    app.run()
