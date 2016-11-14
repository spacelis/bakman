#!/usr/bin/env python2
"""
File: marker.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
"""
# pylint: disable-msg=too-few-public-methods

import logging
from datetime import datetime
from dateparser import parse as dtparse
from grouper import MetaGrouper


logger = logging.getLogger(__name__)


class MetaMarker(type):

    """ A meta class for different types of markers."""

    marker_type = dict()

    def __init__(cls, name, bases, dct):
        """ Adding subclasses to markers dict
        """
        if name != 'Marker':
            MetaMarker.marker_type[dct['__marker_name__']] = cls
        super(MetaMarker, cls).__init__(name, bases, dct)


class Marker(object):

    """ A function for marking the timeseries. """

    __metaclass__ = MetaMarker

    def __call__(self, timeseries):
        """ Return a marking of the timeseries.

        :timeseries: TODO
        :returns: TODO

        """
        raise NotImplementedError

    @classmethod
    def from_rule(cls, dct):
        """TODO: Docstring for from_rule.

        :dct: TODO
        :returns: TODO

        """
        if cls is Marker:
            mtype = MetaMarker.marker_type[dct['type']]
            return mtype.from_rule({k: v for k, v in dct.items() if k != 'type'})
        else:
            return cls(**dct)


class DateRangeMarker(Marker):

    """Docstring for DateRange. """


    __marker_name__ = 'daterange'

    def __init__(self, start='100 years ago', end='now'):
        """TODO: to be defined1. """
        Marker.__init__(self)
        if start is None and end is None:
            raise ValueError('Need either start or end.')
        if not isinstance(start, datetime):
            start = dtparse(start)
        self._start = start

        if not isinstance(end, datetime):
            end = dtparse(end)
        self._end = end

    def __call__(self, timeseries):
        return [self._start <= d <= self._end for d in timeseries]


class CompositeMarker(Marker):

    """Docstring for CompositeMarker. """


    __marker_name__ = 'composite'

    def __init__(self, markers, disjoint=True):
        """TODO: to be defined1.

        :markers: TODO
        :disjoint: TODO
        """
        Marker.__init__(self)


        self._markers = markers
        self._disjoint = disjoint

    def __call__(self, timeseries):

        if self._disjoint:
            agg = any
        else:
            agg = all
        return [agg(x) for x in zip(*[mkr(timeseries) for mkr in self._markers])]

    @classmethod
    def from_rule(cls, dct):
        """TODO: Docstring for fromDict.

        :arg1: TODO
        :returns: TODO

        """
        markers = [Marker.from_rule(m) for m in dct['markers']]
        return cls(markers, dct.get('disjoint', True))


class GroupedMarker(Marker):

    """ Grouping datetime series into a specific group. """

    __marker_name__ = 'grouped'

    def __init__(self, grouper, keep='first'):
        """ Initialize the datastruct with a series of datetimes.
            :keep: keep which in a group
        """
        self._grouper = grouper
        self._keep = keep

    def mark_offset(self, i, timeseries):
        """ Mark the first in each groups

        :i: The offset of the mark
        :timeseries: TODO
        :returns: self

        """
        marks = [False for _ in range(len(timeseries))]
        for grp in self._grouper(timeseries):
            if i < len(grp):
                marks[grp[i]] = True
            else:
                logger.warn('The offset is out of bound.')
        return marks

    def __call__(self, timeseries):
        if self._keep == 'first':
            return self.mark_offset(0, timeseries)
        elif self._keep == 'last':
            return self.mark_offset(-1, timeseries)
        else:
            raise NotImplementedError


    @classmethod
    def from_rule(cls, dct):
        """TODO: Docstring for from_rule.

        :dct: TODO
        :returns: TODO

        """
        grouper_dict = dct['grouper']
        gtype = MetaGrouper.grouper_type[grouper_dict['type']]
        grouper = gtype.from_rule({k: v for (k, v) in grouper_dict.items() if k != 'type'})
        return cls(grouper, keep=dct.get('keep', 'first'))
