"""Run a test multiple times to see if it's flaky."""

import pytest
import time

DEFAULT_FLAKE_RUNS = 50
DEFAULT_FLAKE_MINUTES = 0


def pytest_addoption(parser):
    """Add options for flakefinder plugin."""
    group = parser.getgroup('flakefinder')

    group.addoption("--flake-finder",
                    action='store_true',
                    dest="flake_finder_enable",
                    default=False,
                    help="create multiple copies of all the selected tests.")
    group.addoption("--flake-runs",
                    action='store',
                    dest="flake_runs",
                    default=DEFAULT_FLAKE_RUNS,
                    type=int,
                    metavar="runs",
                    help="number of times to repeat the tests. (default: %default)")
    group.addoption("--flake-max-minutes",
                    action="store",
                    dest="flake_max_minutes",
                    default=DEFAULT_FLAKE_MINUTES,
                    type=int,
                    metavar="minutes",
                    help="Don't run for longer than this parameter. (default: %default)")

def pytest_configure(config):
    """Register the plugin if needed."""
    if config.getoption('flake_finder_enable'):
        config.pluginmanager.register(FlakeFinderPlugin(config))


class FlakeFinderPlugin(object):
    """This is a pytest plugin that multiplies all selected tests by `flake_runs`."""

    def __init__(self, config):
        self.flake_runs = config.getoption('flake_runs')
        self.expires = config.getoption('flake_max_minutes')
        if self.expires:
            self.expires = time.time() + self.expires * 60

    @pytest.mark.tryfirst
    def pytest_generate_tests(self, metafunc):
        """For all true pytest tests use metafunc to add all the duplicates."""
        # This is safer because otherwise test with fixtures might not be setup correctly.
        # Parameterization requires the test function to accept the permutation as
        # either an argument or depend on it as a fixture. Use fixture so the test
        # function signature is not changed. Prefix with underscores and suffix with
        # function name to reduce odds of collision with other fixture names.
        fixture_name = '__flakefinder_{}'.format(metafunc.function.__name__)
        metafunc.fixturenames.append(fixture_name)
        metafunc.parametrize(
            argnames=fixture_name,
            argvalues=list(range(self.flake_runs)),
        )
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

    def pytest_runtest_call(self, item):
        """Skip tests if we've run out of time."""
        if self.expires and self.expires < time.time():
            pytest.skip("time bound exceeded")
