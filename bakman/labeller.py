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
from collections import OrderedDict
from datetime import datetime
from itertools import groupby
from dateparser import parse as dtparse


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


def mk_key_extractor(regex, group=1):
    """TODO: Docstring for mk_key_extractor.

    :regex: TODO
    :returns: TODO

    """
    _regex = re.compile(regex)
    if _regex.groups < group:
        raise ValueError('The group index is out of bound.')
    def _extractor(astring):
        mat = _regex.match(astring)
        if mat is not None:
            return mat.group(1)
        return None
    return _extractor

class RegexLabeller(Labeller):

    """Docstring for RegexLabeller. """

    def __init__(self, regex, files):
        """TODO: to be defined1.

        :regex: TODO

        """
        self._regex = re.compile(regex)
        key_extr = mk_key_extractor(self._regex)
        ft_pairs = [(f, dtparse(key_extr(f)))
                    for f in files
                    if key_extr(f)]
        super(RegexLabeller, self).__init__(ft_pairs)


class StatLabeller(Labeller):

    """ Labelling the file with the data time from file metadata."""

    def __init__(self, files, mode='m'):
        """

        :mode: TODO

        """
        self._mode = mode
        tag = 'st_{0}time'.format(self._mode)
        ft_pairs = [(f, datetime.fromtimestamp(getattr(os.stat(f), tag)))
                    for f in files]
        super(StatLabeller, self).__init__(ft_pairs)


class BinderLabeller(object):

    """Docstring for BinderLabeller. """

    def __init__(self, files, group_ptn, base=None):
        """TODO: to be defined1.

        :files: TODO
        :base: TODO

        """
        gkey_extr = mk_key_extractor(group_ptn)
        super(BinderLabeller, self).__init__()
        groupable_files = [f for f in files if gkey_extr(f)]
        self._group_ptn = re.compile(group_ptn)
        self._groups = OrderedDict()
        for _, grp in groupby(sorted(groupable_files, key=gkey_extr), key=gkey_extr):
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
