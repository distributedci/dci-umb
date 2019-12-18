import json

from proton import Message


class Event(object):
    def __init__(self, body):
        self.message = Message(body=json.dumps(body).encode('utf-8'))
