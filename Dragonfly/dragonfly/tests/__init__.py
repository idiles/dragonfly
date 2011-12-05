# -*- coding: UTF-8 -*-
#
# A2.LT
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#

import urllib
import unittest
import os
import sha

import cherrypy
import turbogears
from turbogears import testutil, database
import inspect
import sqlobject
from sqlobject.inheritance import InheritableSQLObject

from dragonfly.controllers import Root

def setup():
    """Set up testing environment."""

#    for item in model.__dict__.values():
#        if inspect.isclass(item) and issubclass(item,
#            sqlobject.SQLObject) and item != sqlobject.SQLObject \
#            and item != InheritableSQLObject:
#            item.createTable(ifNotExists=True)
#            item.clearTable()

    cherrypy.root = Root()

#    Visit.createTable(ifNotExists=True)
    #testutil.create_request('/')

#    for group in ['admin', 'member']:
#        if Group.selectBy(group_name=group).count() == 0:
#            Group(group_name=group, display_name=group)

#    if User.selectBy(user_name='mgr').count() == 0:
#        user = User(user_name='mgr', email_address='mgr@a2.lt',
#            display_name='Admin', password='mgr',
#            phone='+37032154321')
#        group = Group.selectBy(group_name=u'admin')[0]
#        group.addUser(user)

#    if User.selectBy(user_name='usr').count() == 0:
#        user = User(user_name='usr', email_address='usr@a2.lt',
#            display_name='User', password='usr',
#            phone='+37011154321')
#        group = Group.selectBy(group_name=u'member')[0]
#        group.addUser(user)

#    Currency(name='LTL', description='Lietuvos Litai')

#    Configuration(name='sms.reply.account_empty',
#        value=u'Jusu saskaitoje nepakanka pinigu nurodytai operacijai atlikti.')
#    Configuration(name='sms.reply.song_not_found',
#        value=u'Daina kodu "%s" nerasta. Patikrinkite dainos koda.')
#    Configuration(name='sms.reply.song_ordered',
#        value=u'Daina "%s - %s" uzsakyta.')
#    Configuration(name='sms.reply.song_ordered_auto',
#        value=u'Daina "%s - %s" uzsakyta. Ji skambes po %s.')


def teardown():
    try:
        turbogears.startup.stopTurboGears()
    except Exception, e:
        pass

