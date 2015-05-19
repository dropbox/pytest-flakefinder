"""Run a test multiple times to see if it's flaky."""
import pytest

def pytest_addoption(parser):
    """Register for arguments."""
    group = parser.getgroup('flakefinder')
    group.addoption("--flake-finder", dest="flake_finder_enable",
                    action='store_true', default=False,
                    help="Enable flake finder.  This will create multiple copies of all the selected tests.")
    group.addoption("--no-flake-finder", dest="flake_finder_enable", action='store_false')
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

    @pytest.mark.trylast
    def pytest_collection_modifyitems(self, items):
        """Multiply those tests!"""
        items[:] = items * self.flake_runs
