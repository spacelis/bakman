#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_marker
----------------------------------

Tests for `marker` module.
"""

import pytest

from bakman import marker
from dateutil.parser import parse as dtparse


def test_daterange_marker():
    """ Test DaterangeMarker
    """
    dates = [dtparse(d)
             for d in ['2016-11-1', '2016-11-2', '2016-11-3', '2016-11.4']]
    marks = dict(DaterangeMarker(start='2016-11-2', end='2016-11-3')(dates))
    assert marks['2016-11-1']



