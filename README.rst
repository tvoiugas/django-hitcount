django-hitcount
===============

.. image:: https://github.com/thornomad/django-hitcount/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/thornomad/django-hitcount/actions/workflows/ci.yml
.. image:: https://img.shields.io/pypi/v/django-hitcount.svg
    :target: https://pypi.org/project/django-hitcount/
.. image:: https://img.shields.io/pypi/pyversions/django-hitcount.svg
    :target: https://pypi.org/project/django-hitcount/

Basic app that allows you to track the number of hits/views for a particular object.

Supports Django 5.2 (LTS), 6.0 and 6.1 on Python 3.10+.

Quick start
-----------

.. code-block:: bash

    pip install django-hitcount

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        ...
        "hitcount",
    ]

    # urls.py
    urlpatterns = [
        ...
        path("hitcount/", include("hitcount.urls", namespace="hitcount")),
    ]

.. code-block:: bash

    python manage.py migrate

Then count and display hits in a template, no JavaScript library required:

.. code-block:: html+django

    {% load hitcount_tags %}
    {% get_hit_count for post %} views
    {% insert_hit_count_js for post %}

Documentation:
--------------

`<https://django-hitcount.readthedocs.io>`_

Source Code:
------------

`<https://github.com/thornomad/django-hitcount>`_

Issues
------

Use the GitHub `issue tracker`_ for django-hitcount to submit bugs, issues, and feature requests.

Changelog
---------

`<https://django-hitcount.readthedocs.io/en/latest/changelog.html>`_

.. _issue tracker: https://github.com/thornomad/django-hitcount/issues
