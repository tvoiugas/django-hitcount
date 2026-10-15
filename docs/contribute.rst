Contribution and Testing
========================

I would love to make it better.  Please fork, branch, and push.

Please make new features/improvements against the develop branch.  If you are patching a bug or providing a fix of some sort that can be made against the master branch.  For larger features, please create your own feature branch first before you make the pull request.

.. note:: You can safely ignore the ``devel`` branch which is old and stale but has something in it I can't remember why I'm saving it.  Call me a hoarder.

Testing
-------

Development dependencies are declared as `dependency groups`_ in ``pyproject.toml`` (pip >= 25.1)::

    $ python -m venv .venv && source .venv/bin/activate
    $ pip install -e . --group dev
    $ pytest            # against your currently installed version of Django
    $ ruff check .      # linting
    $ tox               # against the entire array of Django/Python versions
    $ tox -e py-dj52    # a single Django version, using the current Python

To run the suite against PostgreSQL instead of SQLite (``pip install "psycopg[binary]"``)::

    $ docker run -d --rm -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=hitcount postgres:17
    $ HITCOUNT_TEST_DB=postgres POSTGRES_PASSWORD=postgres pytest
    $ POSTGRES_PASSWORD=postgres tox -e py-dj61-pg   # or through tox

The browser (Selenium) tests are opt-in::

    $ pip install --group selenium
    $ HITCOUNT_SELENIUM=1 pytest -m selenium  # set HITCOUNT_SELENIUM_BROWSER=firefox|edge to switch browser

If you change a model, remember to add a migration; the test-suite fails when one is missing.

.. _dependency groups: https://packaging.python.org/en/latest/specifications/dependency-groups/
