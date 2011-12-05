# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Test service model

from elixir import *

class Something(Entity):
    using_options(tablename='thing')

    title = Field(Unicode(30))
    description = Field(UnicodeText)
