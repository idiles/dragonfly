# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Test service model

from elixir import *

class SomethingElse(Entity):
    using_options(tablename='something_else')

    title = Field(Unicode(30))
    description = Field(UnicodeText)
