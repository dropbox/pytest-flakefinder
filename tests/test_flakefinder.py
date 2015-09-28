"""Tests for the flakefinder plugin."""
import pytest
import pytest_flakefinder

def test_help_message(testdir):
    """Test that the options don't change names."""
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'flakefinder:',
        '*--flake-finder*',
        '*--flake-runs=runs*',
        '*--flake-max-minutes=minutes*',
    ])

@pytest.mark.parametrize("flags, runs", [
    ([], pytest_flakefinder.DEFAULT_FLAKE_RUNS),
    (["--flake-runs=1"], 1),
    (["--flake-runs=25"], 25),
])
def test_repeat_success(testdir, flags, runs):
    """Test that pytest-style tests are duplicated correctly."""

    # The test file.
    testdir.makepyfile("""
        def test():
            assert True
    """)

    # Run pytest.
    flags += ['--flake-finder', '-v']
    result = testdir.runpytest(*flags)

    # Check output.
    result.stdout.fnmatch_lines(
        ['collecting ... collected %d items' % runs] +
        # fnmatch doesn't like `[` characters so I use `?`.
        ['*::test?%d? PASSED' % i for i in range(runs)]
    )
    assert result.ret == 0

@pytest.mark.parametrize("flags, runs", [
    ([], pytest_flakefinder.DEFAULT_FLAKE_RUNS),
    (["--flake-runs=1"], 1),
    (["--flake-runs=25"], 25),
])
def test_unittest_repeats(testdir, flags, runs):
    """Test that flake-finder works with unittest.TestCase."""

    # The test file.
    testdir.makepyfile("""
        import unittest

        class TestAwesome(unittest.TestCase):
            def test(self):
                assert True
     """)

    # Run pytest.
    flags += ['--flake-finder', '-v']
    result = testdir.runpytest(*flags)

    # Check output.
    result.stdout.fnmatch_lines(
        # NB: unitest TestCases don't increment the collected items.
        ['collecting ... collected 1 items'] +
        ['*::TestAwesome::test PASSED' for _ in range(runs)]
    )
    assert result.ret == 0

@pytest.mark.parametrize("flags, runs", [
    (["--flake-runs=10"], 10),
    (["--flake-runs=25"], 25),
    ([], pytest_flakefinder.DEFAULT_FLAKE_RUNS),
])
def test_flaky_test(testdir, flags, runs):
    """Test that flaky tests fail the tests."""
    # This test will fail on the 20th call
    testdir.makepyfile("""
        count = [-1]
        def test():
            count[0] += 1
            assert count[0] != 20
    """)

    # Run pytest.
    flags += ['--flake-finder', '-v']
    result = testdir.runpytest(*flags)

    # Check output.
    result.stdout.fnmatch_lines(
        ['collecting ... collected %d items' % runs] +
        ['*::test?%d? PASSED' % i for i in range(min(runs, 20))] +
        ['*::test?%d? FAILED' % i for i in range(20, min(runs, 21))] +
        ['*::test?%d? PASSED' % i for i in range(21, runs)]
    )
    assert result.ret == 0 if runs < 20 else 1

def test_parametrized_tests(testdir):
    """Test that parametrized tests get multiplied correctly too."""
    testdir.makepyfile("""
        import pytest

        @pytest.mark.parametrize("number", (1, 5, 10))
        def test(number):
            assert number
    """)

    # Run pytest.
    flags = ['--flake-finder', '-v']
    result = testdir.runpytest(*flags)

    # Check output.
    result.stdout.fnmatch_lines(
        ['collecting ... collected 150 items'] +
        ['*::test?%d-%d? PASSED' % (i, x)
         for i in range(pytest_flakefinder.DEFAULT_FLAKE_RUNS)
         for x in [1, 5, 10]]
    )
    assert result.ret == 0

@pytest.mark.parametrize("minutes", (1, 5, 10))
def test_flake_max_minutes(testdir, minutes):
    """Test --flake-max-minutes= option."""
    # On the 10th iteration we monkey-patch time.time to advance time past the
    # limit.
    testdir.makepyfile("""
        import time

        count = [1]
        def test():
            if count[0] == 10:
              cur_time = time.time()
              # Move time 1 second past the limit at least.
              time.time = lambda: cur_time + %d * 60 + 1
            count[0] += 1
    """ % minutes)

    # Run pytest.
    result = testdir.runpytest('--flake-finder', '-v', '--flake-max-minutes=%d' % minutes, '-s')

    passing_runs = 10
    runs = pytest_flakefinder.DEFAULT_FLAKE_RUNS

    # Check output.
    result.stdout.fnmatch_lines(
        # fnmatch doesn't like `[` characters so I use `?`.
        ['collecting ... collected %d items' % runs] +
        ['*::test?%d? PASSED' % i for i in range(min(runs, passing_runs))] +
        ['*::test?%d? SKIPPED' % i for i in range(passing_runs, runs)]
    )
    assert result.ret == 0

def test_flake_derived_classes(testdir):
    """Tests that if two tests share the same function they still get duped properly."""

    testdir.makepyfile("""
    import unittest

    class Base(object):
        def runTest(self):
            pass

    class TestMoreAwesome(Base, unittest.TestCase):
        pass

    class TestAwesome(Base, unittest.TestCase):
        pass
    """)

    # Run pytest.
    flags = ['--flake-finder', '-v', '-k', 'TestAwesome']
    result = testdir.runpytest(*flags)

    # Check output.
    result.stdout.fnmatch_lines(
        # NB: unitest TestCases don't increment the collected items.
        ['collecting ... collected 2 items'] +
        # The bug was that TestAwesome wouldn't run multiple times.
        ['*::TestAwesome::runTest PASSED'
         for _ in range(pytest_flakefinder.DEFAULT_FLAKE_RUNS)]
    )
    assert result.ret == 0
