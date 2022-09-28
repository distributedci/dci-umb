import json
import logging
import requests


logger = logging.getLogger(__name__)


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
        try:
            json = {
                "headers": event.message.properties,
                "msg": json.loads(body),
            }
            requests.post(self.destination, json=json)
        except ValueError:
            logger.error("Can't json load event message body: %s" % body)
