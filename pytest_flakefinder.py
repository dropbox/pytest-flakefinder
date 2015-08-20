"""Run a test multiple times to see if it's flaky."""

from __future__ import absolute_import

import pytest

import time


def pytest_addoption(parser):
    """Register for arguments."""
    group = parser.getgroup('flakefinder')
    group.addoption("--flake-finder", dest="flake_finder_enable",
                    action='store_true', default=False,
                    help="Enable flake finder.  This will create multiple copies of all the selected tests.")
    group.addoption("--no-flake-finder", dest="flake_finder_enable", action='store_false')
    group.addoption("--flake-max-minutes", dest="flake_max_minutes", default=0, type=int, action="store",
                    help="Don't run for longer than this parameter. Default is 0, which is no limit")
    group.addoption("--flake-runs", metavar="flake_runs",
                    action='store', dest="flake_runs", type=int, default=50)

def pytest_configure(config):
    """Register the plugin if needed."""
    if config.getoption('flake_finder_enable'):
        config.pluginmanager.register(FlakeFinderPlugin(config))

class FlakeFinderPlugin(object):
    """This is the flake finder plugin.  It multiplies all selected tests by flake_runs.

    Args:
       config: The config values passed to the plugin.
    """

    def __init__(self, config):
        self.flake_runs = config.getoption('flake_runs')
        self.expires = config.getoption('flake_max_minutes')
        if self.expires:
            self.expires = time.time() + self.expires * 60

    @pytest.mark.trylast
    def pytest_collection_modifyitems(self, items):
        """Multiply those tests!"""
        items[:] = items * self.flake_runs

    def pytest_runtest_call(self, item):
        # if we run out of time, skip the rest of the tests in
        # the test plan
        if self.expires and self.expires < time.time():
            pytest.skip("time bound exceeded")
