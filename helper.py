# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly helper functions

from datetime import date, time, datetime, timedelta
import simplejson
from simplejson import loads, dumps, JSONEncoder, JSONDecoder

from idileslib.utils import strptime

__all__ = ['to_json', 'from_json']

DATETIME_FORMAT = '%Y-%m-%d %H-%M-%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            json = obj.strftime(DATETIME_FORMAT)
            if obj.microsecond != 0:
                json = '%s.%d' % (json, obj.microsecond)
            return dict(__type__='__datetime__', value=json)
        elif isinstance(obj, date):
            return dict(__type__='__date__', value=obj.strftime(DATE_FORMAT))
        elif isinstance(obj, time):
            json = obj.strftime(TIME_FORMAT)
            if obj.microsecond != 0:
                json = '%s.%d' % (json, obj.microsecond)
            return dict(__type__='__time__', value=json)
        return super(CustomEncoder, self).default(obj)

def custom_decoder(value):
    if '__type__' in value:
        if value['__type__'] == '__datetime__':
            value = value['value']
            if '.' in value:
                _datetime, microsecond = value.split('.')
                _datetime = strptime(_datetime, DATETIME_FORMAT)
                _datetime += timedelta(microseconds=int(microsecond))
                return _datetime
            else:
                return strptime(value, DATETIME_FORMAT)
        elif value['__type__'] == '__date__':
            return strptime(value['value'], DATE_FORMAT).date()
        elif value['__type__'] == '__time__':
            value = value['value']
            if '.' in value:
                _time, microsecond = value.split('.')
                _time = strptime(_time, TIME_FORMAT)
                _time += timedelta(microseconds=int(microsecond))
                return _time.time()
            else:
                return strptime(value, TIME_FORMAT).time()
    return value

# The c version treats strings differently. Use py version
py_scanstring = simplejson.decoder.py_scanstring
scanstring = simplejson.decoder.scanstring

decoder = JSONDecoder(object_hook=custom_decoder)
decoder.parse_string = py_scanstring
decoder.scan_once = simplejson.scanner.py_make_scanner(decoder)


def to_json(value):
    return dumps(value, cls=CustomEncoder)

def from_json(json):
    # Replace the original scanstring
    simplejson.decoder.scanstring = py_scanstring
    val = decoder.decode(json)
    # Put back the original
    simplejson.decoder.scanstring = scanstring
    return val
