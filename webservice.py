# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly WebService module


from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError, URLError

from helper import from_json, to_json
from testing import is_testing, get_testing_server


def callservice(url__, headers__=None, **kargs):
    if not is_testing():
        kw = {} 
        if headers__:
            kw['headers'] = headers__
        if kargs:
            # urlencode does not accept non-ascii data
            for k, v in kargs.iteritems():
                if isinstance(v, unicode):
                    kargs[k] = v.encode('utf-8')
            kw['data'] = urlencode(kargs)
        req = Request(url__, **kw)
        u = urlopen(req)
        return u.read()
    else:
        from paste.fixture import AppError

        headers = {}
        if headers__:
            headers.update(headers__)
        try:
            resp = get_testing_server().post(url=url__, headers=headers,
                params=kargs).body
            return resp
        except AppError, e:
            if '500' in e.message:
                raise ValueError(e.message.split('\n', 1)[1].strip())
            raise


class WebService(object):
    def __init__(self, name__, *args, **kargs):
        super(WebService, self).__init__(*args, **kargs)
        self.__name = name__
        try:
            url = self.__url
        except AttributeError:
            raise AttributeError('The ESB is not set')

        try:
            methods = callservice(url, headers__=self.__headers)
        except HTTPError, e:
            if e.code == 401:
                # Unauthorized
                if self.__key:
                    raise ValueError('The key %s does not grant access to %s' \
                        % (self.__key, self.get_esb()))
                raise ValueError('The access to server %s is unauthorized' % \
                    self.get_esb())
            raise ValueError('The service %s was not found in %s' % (name__,
                self.get_esb()))
        except URLError:
            raise ValueError('The ESB was not found in %s' % (self.get_esb()))

        for method in from_json(methods):
            setattr(self, method, self.__hide(method))

    @property
    def __url(self):
        return self.get_esb() + '/' + self.__name

    def __hide(self, name):
        def method(*args, **kargs):
            url = self.__url + '/' + name
            # Put positional arguments into keyword arguments as we want all the
            # parameters to go through POST
            if args:
                kargs['__dwsargs__'] = args
            for key in kargs.keys():
                kargs[key] = to_json(kargs[key])
            result = callservice(url, headers__=self.__headers, **kargs)
            result = from_json(result)
            return result

        if isinstance(name, unicode):
            name = name.encode('UTF-8')
        method.__name__ = name
        return method

    @property
    def __headers(self):
        headers = {}
        if self.get_key():
            headers['Authorization'] = self.get_key()
        return headers

    @classmethod
    def get_esb(cls):
        return cls.__esb

    @classmethod
    def set_esb(cls, esb, key=None):
        esb = esb.strip().lower()
        esb = esb.rstrip('/')
        cls.__esb = esb
        cls.__key = key

    @classmethod
    def get_key(cls):
        try:
            return cls.__key
        except:
            return None

    def __repr__(self):
        return '<WebService %s at %s>' % (self.__name, self.get_esb())
