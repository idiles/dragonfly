# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 IDILES SYSTEMS, UAB
#
# Dragonfly helper tests


def test_from_to_json():
    r"""Test conversion from/to json.

    Set up

        >>> from dragonfly import from_json, to_json
        >>> def check(vars):
        ...     for var in vars:
        ...         json = to_json(var)
        ...         if not isinstance(json, str):
        ...             print 'Value %s is not str' % repr(json)
        ...         jvar = from_json(json)
        ...         if var != jvar:
        ...             print '%s != %s' % (repr(var), repr(jvar))
        ...         if type(var) != type(jvar):
        ...             print '%s of type %s != %s of type %s' % (repr(var),
        ...                 type(var), repr(jvar), type(jvar))

    Test variables of simple types. All strings are converted to unicode

        >>> bools = (False, True)
        >>> ints = (0, 0, -1, -12334657, 3425132)
        >>> floats = (0.0, -1.2, 3.1415, 10 / 3.0)
        >>> strs = (u'a', u'some\nstring', u'Čia lietuviškos raidės')

    And some complex types. The tuple is treated as a list so we do not include
    it

        >>> from datetime import date, time, datetime
        >>> dates = (date(1996, 2, 29), time(23, 58), time(5, 8, 12, 456),
        ...     datetime(2001, 9, 11, 11, 15, 36, 22111))
        >>> cplx = ([], {})

        >>> vars = (None,) + bools + ints + floats + strs + dates + cplx

    First, bare variables

        >>> check(vars)

    Now try including these variables into arrays various ways

        >>> check([(v) for v in vars])
        >>> check([[v] for v in vars])
        >>> check([{'var': v} for v in vars])

        >>> check([[[v], (v), {'var': v}] for v in vars])

    """
