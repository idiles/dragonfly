# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly testing module

import sys
from elixir import cleanup_all

__testing = False
__server = None

def setup(module=None, config_file='test.cfg', custom_config=None):
    # Shut logging up
    import logging
    logging.disable(100)

    from paste.fixture import TestApp
    from dragonfly import Dragonfly
    df = Dragonfly(config_file=config_file, custom_config=custom_config)
    global __server
    __server = TestApp(df)
    global __testing
    __testing = True

    from webservice import WebService
    WebService.set_esb(df.config.get('controller'),
        key=df.config.get('access_key'))

def teardown(module=None):
    global __server
    services = __server.app.services

    cleanup_all(drop_tables=True)
    # Elixir entities are setup only after import. As the service modules are
    # imported once per nosetest session, after the cleanup_all they are not set
    # up again. We need to 'export' service modules so that elixir would import
    # and set them up again
    keys = []
    for service in services.itervalues():
        name = service['modulename']
        for key in sys.modules:
            if key == name or key.startswith('%s.' % name):
                keys.append(key)
    for key in keys:
        if key in sys.modules:
            del sys.modules[key]

def get_testing_server():
    if not is_testing():
        raise ValueError('Testing environment not set up')
    return __server

def is_testing():
    return __testing
