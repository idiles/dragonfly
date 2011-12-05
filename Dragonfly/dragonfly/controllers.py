from datetime import datetime
from sqlalchemy import desc
import turbogears as tg
from turbogears import controllers, expose, flash, paginate
from turbogears import identity, redirect
from cherrypy import request, response
import cherrypy

from idileslib.data import DataObject

from dragonfly import model
from dragonfly.model import WebServiceLog
from dragonfly.services import ServicesController

class AdminController(controllers.Controller):

    @expose(template="dragonfly.templates.admin.index")
    @identity.require(identity.in_group("admin"))
    def index(self):
        items = sorted(cherrypy.root.services.services.items())
        services = []
        for i in items:
            r = i[1]
            s = DataObject()
            s.title = "%s %s" % (r.title, r.version)
            s.name = r.name
            s.status = r.status
            s.started = r.started.strftime('%Y-%m-%d %H:%M:%S')

            now = datetime.now()
            thismin = datetime(now.year, now.month, now.day, now.hour, 
                now.minute)
            s.avgduration = WebServiceLog.query.filter_by(
                name=s.name).avg(WebServiceLog.c.duration)
            if s.avgduration:
                s.rps = int(1. / s.avgduration)
                load = (WebServiceLog.query.filter(\
                    "name=:name and date>=:date").params(\
                    name=r.name, date=thismin).count() \
                    * 100) / (60 * 100 * s.avgduration)
                if load > 100:
                    load = 100
                s.load = "%.2f" % load
                s.avgduration = "%.4f" % s.avgduration
            else:
                s.rps = '--'
                s.load = '0.00'
                s.avgduration = '--'
            s.requests = WebServiceLog.query.filter_by(name=s.name).count()
            services.append(s)
        return dict(services=services)

    @expose(template="dragonfly.templates.admin.service")
    @identity.require(identity.in_group("admin"))
    @paginate('log', limit=100)
    def service(self, name):
        items = sorted(cherrypy.root.services.services.items())
        service = cherrypy.root.services.services[name]
        log = WebServiceLog.query.filter_by(name=name).order_by(desc('date'))
        return dict(service=service, log=log)


class Root(controllers.RootController):

    services = ServicesController(model=model)
    admin = AdminController()

    @expose(template="dragonfly.templates.index")
    @identity.require(identity.in_group("admin"))
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        flash("Your application is now running")
        return dict(now=time.ctime())

    @expose(template="dragonfly.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted() \
                and not identity.get_identity_errors():
            raise redirect(tg.url(forward_url or previous_url or '/', kw))

        forward_url = None
        previous_url = request.path

        if identity.was_login_attempted():
            msg = _("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg = _("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg = _("Please log in.")
            forward_url = request.headers.get("Referer", "/")

        response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=request.params, forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
