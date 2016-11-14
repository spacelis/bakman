#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_marker
----------------------------------

Tests for `marker` module.
"""

import pytest

from contextlib import contextmanager
from click.testing import CliRunner

from bakman import bakman
from bakman import cli


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'bakman.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
