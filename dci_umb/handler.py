import json
import requests


class Handler(object):
    @staticmethod
    def is_interested_in(event):
        raise NotImplementedError

    def handle_event(self, event):
        raise NotImplementedError


class HTTPBouncerMessageHandler(Handler):
    def __init__(self, destination):
        self.destination = destination

    @staticmethod
    def is_interested_in(event):
        return True

    def handle_event(self, event):
        body = event.message.body.decode("utf-8")
        properties = event.message.properties.decode("utf-8")
        requests.post(
            self.destination,
            json={"headers": json.loads(properties), "msg": json.loads(body)},
        )
