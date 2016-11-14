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


class Labeller(object):

    """ Labelling non-usefuls"""

    def __init__(self, ft_pairs):
        """TODO: to be defined1.

        :files: TODO

        """
        self._files, self._timestamps = zip(*sorted(ft_pairs, key=lambda x: x[1]))

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
        return self._timestamps


class RegexLabeller(Labeller):

    """Docstring for RegexLabeller. """

    def __init__(self, regex, files):
        """TODO: to be defined1.

        :regex: TODO

        """
        self._regex = re.compile(regex)
        ft_pairs = [(f, dtparse(self._regex.match(f).group(1))) for f in files]
        super(RegexLabeller, self).__init__(ft_pairs)


class StatLabeller(Labeller):

    """ Labelling the file with the data time from file metadata."""

    def __init__(self, files, mode='m'):
        """

        :mode: TODO

        """
        self._mode = mode
        tag = 'st_{0}time'.format(self._mode)
        ft_pairs = [(f, datetime.fromtimestamp(getattr(os.stat(f), tag))) for f in files]
        super(StatLabeller, self).__init__(ft_pairs)


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
