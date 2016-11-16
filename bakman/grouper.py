#!/usr/bin/env python2
"""
File: grouper.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
"""
# pylint: disable-msg=too-few-public-methods

from datetime import timedelta
from itertools import groupby

class MetaGrouper(type):

    """ A meta class for different types of markers."""

    grouper_type = dict()

    def __init__(cls, name, bases, dct):
        """ Adding subclasses to markers dict
        """
        if name != 'Grouper':
            MetaGrouper.grouper_type[dct['__grouper_name__']] = cls
        super(MetaGrouper, cls).__init__(name, bases, dct)


class Grouper(object):

    """Docstring for Grouper. """

    __metaclass__ = MetaGrouper

    def __init__(self, key):
        """TODO: to be defined1. """
        self._key = key

    def __call__(self, timeseries):
        return [[i for i, _ in g]
                for _, g in groupby(enumerate(timeseries),
                                    key=lambda x: self._key(x[1]))]

    @classmethod
    def from_rule(cls, dct):
        """TODO: Docstring for from_rule.

        :dct: TODO
        :returns: TODO

        """
        if cls is Grouper:
            return MetaGrouper\
                .grouper_type[dct['type']]\
                .from_rule({k: v for k, v in dct.items() if k != 'type'})
        else:
            return cls(**dct)


class DayGrouper(Grouper):

    """ Grouping datetime into days. """

    __grouper_name__ = 'daily'

    def __init__(self):
        """ Init """
        Grouper.__init__(self, lambda x: x.date())


class WeekGrouper(Grouper):

    """ Grouping datetime into weeks that start on Monday. """

    __grouper_name__ = 'weekly'

    def __init__(self, start_on='mon'):
        """ Init """
        if start_on == 'mon':
            Grouper.__init__(self, lambda x: x.date() - timedelta(days=x.date().weekday()))
        elif start_on == 'sun':
            Grouper.__init__(self, lambda x: x.date() - timedelta(days=x.date().weekday() + 1))


class MonthGrouper(Grouper):

    """ Grouping datetime into months. """

    __grouper_name__ = 'monthly'

    def __init__(self):
        """ Init """
        Grouper.__init__(self, lambda x: x.date() - timedelta(days=x.date().day - 1))


class YearGrouper(Grouper):

    """ Grouping datetime into months. """

    __grouper_name__ = 'yearly'

    def __init__(self):
        """ Init """
        Grouper.__init__(self, lambda x: x.date().year)
