# -*- coding: UTF-8 -*-
#
# Copyright (c) 2008 IDILES SYSTEMS, UAB
#
# Services controller

import os
import sys
import traceback
import time
from datetime import datetime
from simplejson import dumps, loads

from turbogears import controllers, expose, url, redirect
from cherrypy import config, request, response

from idileslib.data import DataObject
from idileslib.soa import ServiceProxy

from dragonfly.model import WebServiceLog


class ServicesController(controllers.Controller):
    """Controller of services.
    """

    def __init__(self, model, *args, **kargs):
        super(controllers.Controller, self).__init__(*args, **kargs)
        self.model = model
        self.services = {}
        base = config.get('services.path')
        ServiceProxy.load_locations(config.get('esb.config.path'))

        esb_services = ServiceProxy.get_locations().keys()

        for d in os.listdir(base):
            if d.startswith('.'):
                continue
            spath = os.path.join(base, d)
            if os.path.isdir(spath):
                try:
                    # TODO: Needs support for directory names like
                    # 'service-0.1'.
                    service = self.import_service(base, d)
                    if not service.name in esb_services:
                        continue
                    if service.model:
                        self.model.__dict__.update(service.model.__dict__)
                    self.services[service.name] = service
                except Exception, e:
                    print "Could not import service %s: %s" % (spath, e.message)

        print "*** Web Services ***"
        for s in self.services.keys():
            print s

        print "*** Web Service locations ***"
        for name, locations in ServiceProxy.get_locations().items():
            print "%s: %s" % (name, ', '.join(locations))

        self.model.init()


    def import_service(self, base, servicedir):
        service = DataObject()

        sys.path.insert(0, base)
        module = __import__(servicedir)
        sys.path.remove(base)

        service_data = module.init()

        service.ServiceClass = service_data['service_class']
        service.name = service_data.get('name', servicedir)
        service.title = service_data.get('title')
        service.version = service_data.get('version')
        service.model = service_data.get('model')

        service.obj = service.ServiceClass()
        service.status = 'Running'
        service.started = datetime.now()

        service.methods = []

        for m in dir(service.obj):
            member = getattr(service.obj, m)
            if 'webmethodtype' in dir(member):
                t = member.__dict__['webmethodtype']
                service.methods.append(m)
                member = expose(member)

        return service


    def reload_service(self, name):
        pass
    

    @expose()
    def default(self, name__, action=None, *args, **kargs):
        if config.get('server.environment') == 'production':
            ip = request.headers['Remote-Addr']
            if ip not in ['::ffff:127.0.0.1']:
                response.status = 300
                return ''

        start_time = time.time()

        response.status = 200
        response.headers['User-Agent'] = 'Idiles Dragonfly Client 1.0'

        if (not name__ in self.services.keys()):
            response.status = 404
            return dict(error=u'Not found: %s' % name__)

        service = self.services[name__].obj

        if action is None and not kargs:
            return dumps(dict(methods=self.services[name__].methods))

        if not action in self.services[name__].methods:
            response.status = 404
            return dumps(dict(error=u"Action not found: %s" % action))

        method = getattr(service, action)

        try:
            resp = dumps(method(**kargs))
        except ValueError, e:
            import traceback
            traceback.print_exc()
            response.status = 200
            resp = dumps(dict(valueerror_=e.message))
        except Exception, e:
            import traceback
            traceback.print_exc()
            response.status = 500
            resp = dumps(dict(error=u'Error: %s' % e.message))

        end_time = time.time()
        duration = time.time() - start_time

        host = request.headers.get('Remote-Addr')
        WebServiceLog(name=name__, action=action, 
            request=None, #request=dumps(kargs),
            response=None, #response=resp, 
            http_status=response.status,
            host=host, duration=duration)

        return resp
        

    @expose()
    def index(self):
        return dumps(dict(services=self.services.keys()))

