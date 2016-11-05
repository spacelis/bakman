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


def load_rules(rulefile, use_json=False):
    """ Load rule file content into a dict.

    :rulefile: TODO
    :returns: TODO

    """
    if use_json:
        import json
        with open(rulefile) as fin:
            return json.load(fin)
    else:
        import yaml
        with open(rulefile) as fin:
            return yaml.load(fin)


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


def print_actions(fout, marks):
    """ Print the action script to the fout

    :fout: TODO
    :returns: TODO

    """
    rm_cnt, keep_cnt = 0, 0
    for f, m in marks:
        fout.write('{0}/bin/rm -f {1}\n'.format('#' if m else '', f))
        rm_cnt += not m
        keep_cnt += m
    fout.write('echo {0} removed and {1} kept.\n'.format(rm_cnt, keep_cnt))


@click.command()
@click.option('-j', '--use-json', is_flag=True,
              help='Use json as input.')
@click.option('-f', '--rulefile', default='BakmanFile',
              help='The rulefile in JSON or YAML.')
@click.option('-r', '--regex', default=None,
              help='The regex for label the date of the file in the filename.')
@click.option('-g', '--group-regex', default=None,
              help='The regex for indicating files belongs to the same backup snapshot.')
@click.option('-o', '--output', default=None,
              help='Output the remove command into a bash script for inspecting.')
@click.argument('files', nargs=-1)
def console(use_json, rulefile, regex, output, group_regex, files):
    """ Parse the rules expressed in a dict object

    :dct: TODO
    :returns: TODO

    """
    rules = load_rules(rulefile, use_json)
    marker = Marker.from_rule(rules)
    if regex is not None:
        labeller = RegexLabeller(files, regex)
    else:
        labeller = StatLabeller(files)

    if group_regex:
        labeller = BinderLabeller(files, group_regex, labeller.__class__)

    if output is not None:
        with open(output, 'w') as fout:
            print_actions(fout, labeller.mark_with(marker))
    else:
        print_actions(sys.stdout, labeller.mark_with(marker))

if __name__ == "__main__":
    console()
