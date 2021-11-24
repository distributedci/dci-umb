import json

from proton import Message


class Event(object):
    def __init__(self, body, properties):
        self.message = Message(
            body=json.dumps(body).encode("utf-8"),
            properties=json.dumps(properties).encode("utf-8"),
        )
