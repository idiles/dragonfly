# This is a test service

from dragonfly import webmethod
import model

local_config = {'test_conf':''}

class TestService(object):
    @webmethod
    def check_parameters(self, param=True):
        return (repr(param), param)

    @webmethod
    def check_parameter_order(self, name, age, married=False, weight=70):
        married = 'married' if married else 'not married'
        return '%s %d %s %.1f' % (name, age, married, weight)

    @webmethod
    def check_config(self):
        return local_config

def init(config):
    global local_config
    local_config = config
    return dict(service_class=TestService, model=model)
