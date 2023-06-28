import json

from proton import Message


class Event(object):
    def __init__(self, body, properties):
        self.message = Message(
            body=json.dumps(body),
            properties=properties,
        )
