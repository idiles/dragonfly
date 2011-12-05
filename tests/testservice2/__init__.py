# This is a test service

from dragonfly import webmethod
import model


class TestService(object):
    @webmethod
    def publicmethod(self):
        return 'I do work'

    def privatemethod(self):
        return "You don't see me"

def init():
    return dict(service_class=TestService, model=model)
