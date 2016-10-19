#!/usr/bin/env python
"""
File: backman.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
"""

import re
import os
import logging
from dateparser import parse as dtparse
from datetime import datetime
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


class RegexLabeller(object):

    """Docstring for RegexLabeller. """

    def __init__(self, regex):
        """TODO: to be defined1.

        :regex: TODO

        """
        self._regex = re.compile(regex)

    def __call__(self, files):
        """TODO: Docstring for label.

        :files: TODO
        :returns: TODO

        """
        return [dtparse(self._regex.match(f).group(1)) for f in files]


class StatLabeller(object):

    """ Labelling the file with the data time from file metadata."""

    def __init__(self, mode='m'):
        """

        :mode: TODO

        """
        self._mode = mode

    def __call__(self, files):
        """TODO: Docstring for label.

        :files: TODO
        :returns: TODO

        """
        tag = 'st_{0}time'.format(self._mode)
        return [datetime.fromtimestamp(getattr(os.stat(f), tag)) for f in files]


@click.command()
@click.option('-j', '--use-json', is_flag=True, help='Use json as input.')
@click.option('-f', '--rulefile', default='BackmanFile', help='The rulefile in JSON or YAML.')
@click.option('-r', '--regex', default=None, help='The regex for label the date of the file in the filename.')
@click.option('-o', '--output', default=None, help='Output the remove command into a bash script for inspecting.')
@click.argument('files', nargs=-1)
def console(use_json, rulefile, regex, output, files):
    """ Parse the rules expressed in a dict object

    :dct: TODO
    :returns: TODO

    """
    rules = load_rules(rulefile, use_json)
    marker = Marker.from_rule(rules)
    if regex is not None:
        labeler = RegexLabeller(regex)
    else:
        labeler = StatLabeller()
    ts, files = zip(*sorted(zip(labeler(files), files), key=lambda x: x[0]))

    marks = marker(ts)
    if output is not None:
        with open(output, 'w') as fout:
            rm_cnt, keep_cnt = 0, 0
            for m, f in zip(marks, files):
                fout.write('{0}/bin/rm -f {1}\n'.format('#' if m else '', f))
                rm_cnt += not m
                keep_cnt += m
            fout.write('echo {0} removed and {1} kept.\n'.format(rm_cnt, keep_cnt))
    else:
        raise NotImplementedError


if __name__ == "__main__":
    console()
