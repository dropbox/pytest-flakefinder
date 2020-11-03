pytest-flakefinder
===================================

.. image:: https://travis-ci.org/dropbox/pytest-flakefinder.png?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/dropbox/pytest-flakefinder

Runs tests multiple times to expose flakiness.

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

* When enabled it will 'multiply' your tests so that they get run multiple times without having to restart pytest.  This helps you find flakiness in your tests.
* You can limit your flake runs to a particular timeout value.


Installation
------------

    pip install pytest-flakefinder

For best flake-finding combine with pytest-xdist::

    pip install pytest-xdist

Usage
-----

Flake Finding
~~~~~~~~~~~~~

Enable plugin for tests::

    pytest --flake-finder

This will run every test the default, 50, times.  Every test is run independently and you can even use xdist to send tests to multiple processes.

To configure the number of runs::

    pytest --flake-finder --flake-runs=runs

To find flakes in one test or a couple of tests you can use pytest's built in test selectiong.

Finding flakes in one test::

    pytest -k test_maybe_flaky --flake-finder

When used with xdist the flake finder can expose many timing related flakes.

Timing Out
~~~~~~~~~~

When using flake-finder as part of a CI run it might be useful to limit the amount of time it will run.

Running with timeout::

    pytest --flake-finder --flake-max-minutes=minutes

Tests started after the timeout will be skipped.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

Contributors
------------
- euresti_
- nipunn1313_
- goodspark_
- and-semakin_
- adaamz_


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/dropbox/pytest-flakefinder/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _euresti: https://github.com/euresti
.. _nipunn1313: https://github.com/nipunn1313
.. _goodspark: https://github.com/goodspark
.. _and-semakin: https://github.com/and-semakin
.. _adaamz: https://github.com/adaamz
