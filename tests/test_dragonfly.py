# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly tests


def test_Dragonfly_serviceconfig():
    r"""Test the service configuration.

    Set up the Dragonfly server without configuration

        >>> from dragonfly import Dragonfly
        >>> df = Dragonfly()

    Set up the Dragonfly server prividing the configuration on the fly
        
        >>> df = Dragonfly(custom_config='''
        ... [services]
        ... [[testservice1]]
        ... path='tests'
        ... dburi='sqlite:///:memory:'
        ... 
        ... [[testservice2]]
        ... path='tests'
        ... dburi='sqlite:///:memory:'
        ... ''')

    Check the service configuration

        >>> for service in sorted(df.services.keys()):
        ...     print service, df.services[service]['path'], \
        ...         df.services[service]['dburi']
        testservice1 tests sqlite:///:memory:
        testservice2 tests sqlite:///:memory:

    Set up the Dragonfly server prividing the configuration in the file

        >>> df = Dragonfly(config_file='tests/test_conf.cfg')

    Check the service configuration

        >>> for service in sorted(df.services.keys()):
        ...     print service, df.services[service]['path'], \
        ...         df.services[service]['dburi']
        testservice2 tests sqlite:///some.db
        testservice3 tests sqlite:///:memory:

    We can combine configuration sources. Custom configuration takes precedence
    over the configuration from the file (notice the dburi of testservice2)

        >>> df = Dragonfly(custom_config='''
        ... [services]
        ... [[testservice1]]
        ... path='tests'
        ... dburi='sqlite:///:memory:'
        ... 
        ... [[testservice2]]
        ... path='tests'
        ... dburi='sqlite:///:memory:'
        ... ''', config_file='tests/test_conf.cfg')

    We get all the options combined

        >>> for service in sorted(df.services.keys()):
        ...     print service, df.services[service]['path'], \
        ...         df.services[service]['dburi']
        testservice1 tests sqlite:///:memory:
        testservice2 tests sqlite:///:memory:
        testservice3 tests sqlite:///:memory:

    """

def test_Dragonfly_selfdescribe():
    r"""Test the ways Dragonfly describes itself.

    Set up the Dragonfly server

        >>> from dragonfly.testing import setup
        >>> from dragonfly import callservice
        >>> setup(None)

    The server has a controller that it listens to (by default - '/services')

        >>> try:
        ...     callservice('/service')
        ... except Exception, e:
        ...     print e.message.split('\n')[0]
        Bad response: 404 Not Found (not 200 OK or 3xx redirect for /service)
        >>> try:
        ...     callservice('/services_and_more')
        ... except Exception, e:
        ...     print e.message.startswith('Bad response: 404')
        True
        >>> resp = callservice('/services')

    The server does not have any services so the description is empty

        >>> callservice('/services')
        '[]'

    Now set up a server that has two services

        >>> setup(config_file='tests/test_conf.cfg',
        ...     custom_config='access_key=None')
        >>> callservice('/services')
        '["testservice2", "testservice3"]'

    Check out one of the services. It has one public method

        >>> callservice('/services/testservice2')
        '["publicmethod"]'
    """

def test_webmethod():
    r"""Test how the webmethods are exposed.

    Set up the Dragonfly server

        >>> from paste.fixture import TestApp
        >>> from dragonfly import Dragonfly
        >>> df = Dragonfly(config_file='tests/test_conf.cfg',
        ...     custom_config='access_key=None')
        >>> server = TestApp(df)
    
    The testservice2 has one web method and one private method. Only the public
    method is exposed
        
        >>> server.get('/services/testservice2').body
        '["publicmethod"]'

        >>> server.get('/services/testservice2/publicmethod').body
        '"I do work"'

    The private method is unreachable
        
        >>> try:
        ...     server.get('/services/testservice2/privatemethod')
        ... except Exception, e:
        ...     print e.message.startswith('Bad response: 404')
        True
    """

def test_model():
    r"""Test the model that Dragonfly creates.

    Set up the Dragonfly server

        >>> from paste.fixture import TestApp
        >>> from dragonfly import Dragonfly
        >>> df = Dragonfly(config_file='tests/test_conf.cfg')

    The 'testservice2' service has an entity Something with
    'using_options(tablename="thing")'. The actual table name should be
    'testservice2_thing'

        >>> from elixir import metadatas

        >>> tablename = 'testservice2_thing'
        >>> for metadata in metadatas:
        ...     if tablename in metadata.tables:
        ...         print tablename
        testservice2_thing

    """

def test_access_key():
    r"""Test the Dragonfly security using the access key.

        >>> from dragonfly.testing import setup
        >>> setup(config_file='tests/test_conf.cfg')
        >>> from dragonfly import WebService

    setup_dragonfly_testing automatically sets the access key so remove it first

        >>> if hasattr(WebService, '_WebService__key'):
        ...     del WebService._WebService__key

    Without the key noone can access the server

        >>> try:
        ...     WebService('testservice2')
        ... except Exception, e:
        ...     print '401 Unauthorized' in e.message
        True

    If we set the key again, we can create the service

        >>> WebService.set_esb('/services', key='ABCD1234')
        >>> WebService('testservice2')
        <WebService testservice2 at /services>
    """
