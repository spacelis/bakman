#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: cli.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description: Commandline interface for Bakman
"""

import sys
import click
from click import BadArgumentUsage
from bakman.labeller import RegexLabeller, StatLabeller, BinderLabeller
from bakman.marker import Marker


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


def print_actions(fout, marks, cmd):
    """ Print the action script to the fout

    :fout: TODO
    :returns: TODO

    """
    rm_cnt, keep_cnt = 0, 0
    for fname, mark in marks:
        if '{}' in cmd or '{0}' in cmd:
            loaded_cmd = cmd.format(fname)
        else:
            loaded_cmd = "{cmd} {filename}".format(cmd=cmd, filename=fname)
        fout.write('{disabled} {loaded_cmd}\n'.format(
            disabled='#' if mark else '', loaded_cmd=loaded_cmd))
        rm_cnt += not mark
        keep_cnt += mark
    fout.write('echo {0} actioned and {1} kept.\n'.format(rm_cnt, keep_cnt))


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
              help='The output file for the compiled commands, if assigned. '
              'Otherwise they go to stdout.')
@click.option('-c', '--command', default='/bin/rm -f',
              help='The action to take for the discarded backup files, default: /bin/rm -f')
@click.argument('files', nargs=-1)  # pylint: disable=too-many-arguments
def console(use_json, rulefile, regex, output, group_regex, command, files):
    """ Parse the rules expressed in a dict object

    :dct: TODO
    :returns: TODO

    """
    try:
        rules = load_rules(rulefile, use_json)
    except IOError:
        raise BadArgumentUsage('Rule file {0} cannot be found.'.format(rulefile))

    marker = Marker.from_rule(rules)

    if len(files) == 1 and files[0] == '-':
        files = [unicode(l.strip()) for l in sys.stdin]
    if len(files) == 0:
        raise BadArgumentUsage(
            'The filenames should be either on stdin (indicated by "-") or as parameters.')

    labeller = StatLabeller(files) if regex is None else RegexLabeller(files, regex)

    if group_regex:
        labeller = BinderLabeller(files, group_regex, labeller.__class__)

    if output is not None:
        with open(output, 'w') as fout:
            print_actions(fout, labeller.mark_with(marker), command)
    else:
        print_actions(sys.stdout, labeller.mark_with(marker), command)


if __name__ == "__main__":
    console()  # pylint: disable=no-value-for-parameter
