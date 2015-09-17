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

    @pytest.mark.tryfirst
    def pytest_generate_tests(self, metafunc):
        """For all true pytest tests use metafunc to add all the duplicates."""
        # This is safer because otherwise test with fixtures might not be setup correctly.
        for _ in xrange(self.flake_runs):
            metafunc.addcall()
        metafunc.function._pytest_duplicated = True

    @pytest.mark.tryfirst
    def pytest_collection_modifyitems(self, items):
        """Add unitest tests to the collection."""
        # Some tests (e.g. unittest.TestCase) don't pass through
        # pytest_generate_tests. For those we use the old "add them multiple
        # times to the items list" trick.
        #
        # Also we want to @tryfirst so that we go before randomizing the list.
        for item in list(items):
            if not getattr(item.function, '_pytest_duplicated', None):
                items.extend([item] * (self.flake_runs - 1))
            item.function._pytest_duplicated = True

    def pytest_runtest_call(self, item):
        # if we run out of time, skip the rest of the tests in
        # the test plan
        if self.expires and self.expires < time.time():
            pytest.skip("time bound exceeded")
