# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# WebService tests



def test_WebService_esb():
    r"""Test the esb setting of WebService.

        >>> from dragonfly import WebService

    # The esb could be set in previous tests. Unset it.

        >>> if '_WebService__esb' in dir(WebService):
        ...     del WebService._WebService__esb

    The esb parameter is the address to the esb server. You must set it to later
    call the WebService

        >>> WebService('some_service')
        Traceback (most recent call last):
        ...
        AttributeError: The ESB is not set

    We must set the esb first

        >>> WebService.set_esb('http://127.0.0.1:445566/serv')
        >>> WebService.get_esb()
        'http://127.0.0.1:445566/serv'

    If we now try to create a WebService we should get an error as the esb does
    not exist there

        >>> try:
        ...     WebService('nonexistant')
        ... except Exception, e:
        ...     'not found' in e.message.lower()
        True
    """

def test_WebService_calls():
    r"""Test how WebService calls the Dragonfly server and the parameters are
    passed.

        >>> from dragonfly import WebService
        >>> from dragonfly.testing import setup
        >>> setup(config_file='tests/test_conf.cfg')

    The server has a service 'testservice3' which has a public method
    'check_parameters'

        >>> service = WebService('testservice3')
        >>> 'check_parameters' in dir(service)
        True

    This method has a parameter 'param' which defaults to True. It returns the
    param's representation and the param itself

        >>> service.check_parameters()
        [u'True', True]

    We can now check various parameters - how they are passed and returned

        >>> params = (None, False, True, 0, 123, -1.2, u'str', [u'list'],
        ...     {u'some': u'dict'})

    Pass them and check that the result matches the parameters. We should get no
    output

        >>> for param in params:
        ...     resp = service.check_parameters(param=param)
        ...     if [repr(param), param] != resp:
        ...         print [repr(param), param], resp

    'testservice3' has a method 'check_parameter_order'. It accepts various
    parameters. We can pass these parameters explicitly

        >>> print service.check_parameter_order(name='Ignas', age=12,
        ...     married=True, weight=81.3)
        Ignas 12 married 81.3

    We can rely on parameter order, just as common Python

        >>> print service.check_parameter_order('Ignas', 12, True, 81)
        Ignas 12 married 81.0

    Or we can even accept the defaults

        >>> print service.check_parameter_order('Ignas', 12)
        Ignas 12 not married 70.0

    This service olso has it's own config what was initialize during init
        >>> service.check_config()
        {u'test_conf': u'it works'}

    """
