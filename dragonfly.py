# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly module


from configobj import ConfigObj
from datetime import datetime
from logging import getLogger
import sys
import time
from traceback import format_exc

from paste.request import path_info_pop, parse_formvars
import elixir
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData

from webservice import WebService
from helper import from_json, to_json
from testing import is_testing


log = getLogger(__name__)

def webmethod(func, type='json'):
    func.webmethod = True
    return func


default_config = """controller='/services'
    path='.'
    dburi='sqlite:///:memory:'
    echo_sql=False
    access_key=None
    [services]"""

service_config_keys = ('path', 'dburi', 'echo_sql')


class Dragonfly(object):
    def __init__(self, config_file=None, custom_config=None):
        load_start = time.time()

        self.config = self.parse_config(config_file, custom_config,
            default_config)

        if self.config.get('server'):
            WebService.set_esb(
                self.config['server'] + self.config['controller'])

        self.load_services()
        
        services = ', '.join(sorted(self.services.keys()))

        self.access_key = self.config.get('access_key')

        load_time = (time.time() - load_start) * 1000

        log.info('Started Dragonfly server in %.2f ms on %s' % (load_time,
            self.config['controller']))
        log.info('Loaded services: %s' % services)

    def parse_config(self, config_file, custom_config=None, default_config=''):
        config = ConfigObj(default_config.split('\n'), unrepr=True)
        # Add configuration from a file
        if config_file:
            try:
                config.merge(ConfigObj(config_file, unrepr=True))
            except TypeError, err:
                log.warn('Configuration file not found at %s' % config_file)
        # Add custom configuration
        if custom_config:
            config.merge(ConfigObj(custom_config.split('\n'), unrepr=True))

        if not config.get('service-config', None):
            config['service-config'] = {}
        c_config = config.get('service-config')
        c_services = config.get('services')
        if c_services:
            # Find all service groups
            servicegroups = filter(lambda s: s.startswith('servicegroup-'),
                c_services.keys())
            # For each service group
            for sg in servicegroups:
                # Recursively parse its configuration
                c_services[sg] = self.parse_config(c_services[sg]['config'])
                # Take its services
                if c_services[sg].get('services'):
                    # And put them one level higher (at our level)
                    c_services.update(c_services[sg].get('services'))
                if c_services[sg].get('service-config'):
                    # Get service-config higher if higher doesn't exist
                    c_services[sg]['service-config'].merge(c_config)
                    c_config.update(c_services[sg]['service-config'])
                    del c_services[sg]['service-config']
                # Then remove the service group
                del c_services[sg]
            # There should be no service groups left in this level
            assert not filter(lambda s: s.startswith('servicegroup-'),
                c_services.keys())
            # Now that we have all services we need to ensure that they get all
            # the missing information that we can provide
            for service in c_services.itervalues():
                for key in service_config_keys:
                    if config.has_key(key) and not service.has_key(key):
                        service[key] = config[key]
        
        return config

    def load_services(self):
        c_services = self.config['services']
        try:
            c_config = self.config['service-config']
        except KeyError:
            c_config = {}

        self.services = {}
        engines = {}
        
        for servicename in filter(lambda s: not s.startswith('servicegroup-'),
            c_services.keys()):
            params = c_services[servicename]

            # Import module
            path = params['path']
            sys.path.insert(0, path)
            module = __import__(servicename)
            sys.path.remove(path)

            params['modulename'] = servicename
            if servicename in c_config:
                service_data = module.init(c_config[servicename])
            else:
                service_data = module.init()
            ServiceClass = service_data['service_class']
            servicename = service_data.get('name', servicename)
            params['service'] = ServiceClass()
            for key in ('title', 'version'):
                params[key] = service_data.get(key)

            # Set up the service model (bind to an engine)
            if 'model' in service_data:
                if params['dburi'] not in engines:
                    engines[params['dburi']] = create_engine(params['dburi'],
                        echo=params['echo_sql'])
                metadata = MetaData()
                metadata.bind = engines[params['dburi']]

                model = service_data['model']
                classes = [getattr(model, c) for c in dir(model)
                    if isinstance(getattr(model, c), type)]
                sql_classes = filter( lambda c: issubclass(c,
                    elixir.Entity) and c != elixir.Entity, classes)
                for cls in sql_classes:
                    desc = cls._descriptor
                    # We are using using_options
                    desc.tablename = '%s_%s' % (servicename, desc.tablename)
                    desc.metadata = metadata

                elixir.metadatas.add(metadata)

            params['status'] = 'Running'
            params['started'] = datetime.now()

            self.services[servicename] = params

        # Bind the default metadata
        if self.config['dburi'] not in engines:
            engines[self.config['dburi']] = create_engine(self.config['dburi'],
                echo=self.config['echo_sql'])
        elixir.metadata.bind = engines[self.config['dburi']]

        elixir.setup_all(create_tables=True)

    def describe(self, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [to_json(sorted(self.services.keys()))]

    def describe_service(self, service, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        service = self.services[service]['service']
        methods = filter(lambda m: getattr(getattr(service, m),
            'webmethod', None), dir(service))
        return [to_json(sorted(methods))]
        
    def not_found(self, start_response):
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['']

    def request_error(self, start_response, error):
        start_response('400', [('Content-Type', 'text/html')])
        if isinstance(error, unicode):
            error = error.encode('utf-8')
        return [error]

    def auth_required(self, start_response):
        start_response('401 Unauthorized', [('Content-Type', 'text/html'),
            ('WWW-Authenticate', '')])
        return ['']

    def __call__(self, environ, start_response):
        base_url = self.config['controller']
        req_url = environ.get('PATH_INFO')
        if not req_url.startswith(base_url + '/') and req_url != base_url:
            return self.not_found(start_response)

        proc_start = time.time()

        try:
            assert self.access_key == environ.get('HTTP_AUTHORIZATION')
            log.debug('Access granted with key %s' % \
                environ.get('HTTP_AUTHORIZATION'))
        except:
            log.warn('Access unauthorized. Environment:\n%s' % environ)
            return self.auth_required(start_response)

        environ['SCRIPT_NAME'] = base_url
        environ['PATH_INFO'] = environ['PATH_INFO'].split(base_url)[1]

        servicename = path_info_pop(environ)
        # Describe myself
        if not servicename:
            desc = self.describe(start_response)
            log.info('Describing esb')
            log.debug('Returning %s' % desc[0])
            return desc

        try:
            service = self.services[servicename]['service']
        except:
            # There is no such service
            log.warn('Service %s not found or not working' % servicename)
            return self.not_found(start_response)
        
        methodname = path_info_pop(environ)
        if not methodname:
            # The request about the service itself
            desc = self.describe_service(servicename, start_response)
            log.info('Describing %s' % servicename)
            log.debug('Returning %s' % desc[0])
            return desc

        # A method was called
        try:
            method = getattr(service, methodname)
            assert getattr(method, 'webmethod', False)
        except:
            # The service does not have such a webmethod
            log.warn('A webmethod %s.%s not found' % (servicename, methodname))
            return self.not_found(start_response)

        kargs = dict()
        try:
            kargs = dict(parse_formvars(environ, include_get_vars=True))
            for karg in kargs.keys():
                kargs[karg] = from_json(kargs[karg])
        except:
            log.warn('Failed to parse parameters for %s.%s: %s' % (servicename,
                methodname, kargs))
            return self.request_error(start_response, 'Invalid parameters')

        # Extract the positional arguments:
        args = kargs.pop('__dwsargs__', [])

        # Call the method
        if is_testing():
            result = method(*args, **kargs)
            result = to_json(result)
        else:
            try:
                exec_start = time.time()
                result = method(*args, **kargs)
                exec_time = (time.time() - exec_start) * 1000

                log.info('%s.%s finished in %.2f ms' % (servicename,
                    methodname, exec_time))
                log.debug('\nArgs: %s\nKargs: %s\nResult: %s' % (args, kargs,
                    result))

                result = to_json(result)
                elixir.session.close()
            except Exception, e:
                exc = format_exc(e)
                start_response('500 Internal Server Error',
                    [('Content-Type', 'text/html')])

                log.error('%s.%s\n%s' % (servicename, methodname, exc))
                elixir.session.close()
                return ['Internal server error']

        start_response('200 OK', [('Content-Type', 'text/html')])

        proc_time = (time.time() - proc_start) * 1000
        log.debug('%s.%s processed in %.2f ms' % (servicename, methodname,
            proc_time))

        return [result]
