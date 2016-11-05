#!/usr/bin/env python
"""
File: bakman.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
"""

import re
import os
import sys
import logging
from collections import OrderedDict
from dateparser import parse as dtparse
from datetime import datetime
from itertools import groupby
import click
from marker import Marker


class Labeller(object):

    """ Labelling non-usefuls"""

    def __init__(self, files):
        """TODO: to be defined1.

        :files: TODO

        """
        self._files = files

    def mark_with(self, marker):
        """TODO: Docstring for mark_with.

        :marker: TODO
        :returns: TODO

        """
        return zip(self._files, marker(self.get_times()))


    def get_times(self):
        """ Return a series of timestamp for files
        :returns: TODO

        """
        raise NotImplementedError


class RegexLabeller(Labeller):

    """Docstring for RegexLabeller. """

    def __init__(self, regex, files):
        """TODO: to be defined1.

        :regex: TODO

        """
        super(RegexLabeller, self).__init__(files)
        self._regex = re.compile(regex)


    def get_times(self):
        """ Extracting timestamp from file names.
        :returns: TODO

        """
        return [dtparse(self._regex.match(f).group(1)) for f in self._files]


class StatLabeller(Labeller):

    """ Labelling the file with the data time from file metadata."""

    def __init__(self, files, mode='m'):
        """

        :mode: TODO

        """
        super(StatLabeller, self).__init__(files)
        self._mode = mode

    def get_times(self):
        """TODO: Docstring for label.

        :files: TODO
        :returns: TODO

        """
        tag = 'st_{0}time'.format(self._mode)
        return [datetime.fromtimestamp(getattr(os.stat(f), tag)) for f in self._files]


class BinderLabeller(object):

    """Docstring for BinderLabeller. """

    def __init__(self, files, group_ptn, base=None):
        """TODO: to be defined1.

        :files: TODO
        :base: TODO

        """
        super(BinderLabeller, self).__init__()
        self._group_ptn = re.compile(group_ptn)
        self._key_func = lambda x: self._group_ptn.match(x).group(1)
        self._groups = OrderedDict()
        for _, grp in groupby(sorted(files, key=self._key_func), key=self._key_func):
            grp = list(grp)
            self._groups[grp[0]] = grp
        self._base = base(self._groups.keys())

    def mark_with(self, marker):
        """ Marking the files"""
        marked = self._base.mark_with(marker)
        return [(f, m) for k, m in marked for f in self._groups[k]]

    def get_times(self):
        """TODO: Docstring for get_times.
        :returns: TODO

        """
        self._base.get_times()
