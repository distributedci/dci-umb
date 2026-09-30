#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
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
import importlib.util
from pathlib import Path

import setuptools


version_path = Path(__file__).parent / "dci_kafka" / "version.py"
version_spec = importlib.util.spec_from_file_location("dci_kafka_version", version_path)
version_module = importlib.util.module_from_spec(version_spec)
version_spec.loader.exec_module(version_module)

setuptools.setup(
    name="dci-kafka",
    version=version_module.__version__,
    packages=setuptools.find_packages(),
    author="Distributed CI team",
    author_email="distributed-ci@redhat.com",
    description="Forward Kafka events to DCI Feeder",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["kafka-python", "python-snappy", "requests"],
    url="https://github.com/redhat-cip/dci-kafka",
    license="Apache v2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
    entry_points={"console_scripts": ["dci-kafka-consumer=dci_kafka.consumer:main"]},
)
