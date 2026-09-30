Changelog
=========

Version 2.0.0
-------------

The first release in several years: it brings the app up to date with current
Django and Python, and ships the fixes that were merged after 1.3.5 but never
released.

**Compatibility**

 * Supports Django 5.2 (LTS), 6.0 and 6.1 on Python 3.10 - 3.14 (Django 6.x needs Python 3.12+)
 * Dropped support for Django < 5.2 and Python < 3.10
 * Removed the ``django-etc`` dependency; Django is now the only requirement

**Upgrade notes**

 * Run ``python manage.py migrate``.  Migration ``0005`` converts every hitcount
   primary key to a ``BigAutoField`` (``bigint``); on a large ``Hit`` table this
   rewrites the table, so plan for it (or run ``hitcount_cleanup`` first)
 * Removed ``hitcount.views._update_hit_count()`` (use ``HitCountMixin.hit_count()``),
   ``hitcount.views.update_hit_count_ajax()`` (use ``HitCountJSONView``) and
   ``hitcount.utils.RemovedInHitCount13Warning``, all deprecated since 1.2
 * ``static/hitcount/hitcount-jquery.js`` (the companion of
   ``{% insert_hit_count_js_variables %}``) no longer needs jQuery; it is kept
   under the same name so existing ``{% static %}`` references keep working.
   ``static/hitcount/jquery.postcsrf.js`` is still shipped
 * ``{% insert_hit_count_js %}`` no longer needs jQuery or ``jquery.postcsrf.js``:
   it uses ``fetch()`` and takes the CSRF token from the template context, so
   ``@ensure_csrf_cookie`` is no longer needed either.  It now dispatches
   ``hitcount:counted`` / ``hitcount:error`` events on ``document``
 * The package metadata now declares the MIT license (matching ``LICENSE``);
   earlier releases wrongly declared BSD

**Fixes**

 * ``get_ip()`` returned the placeholder ``10.0.0.1`` whenever
   ``X-Forwarded-For`` contained a list of proxies; it now uses the first
   (client) address, as documented
 * ``HitCountJSONView`` answers ``400`` for a missing or non-numeric
   ``hitcountPK`` instead of swallowing every exception with a bare ``except``
 * The hit-counting checks use ``.exists()`` instead of fetching rows
 * Invalid ``HITCOUNT_HITCOUNT_MODEL`` values raise ``ImproperlyConfigured``
 * ``{% insert_hit_count_js %}`` and ``{% insert_hit_count_js_variables %}``
   add the request's CSP nonce to their ``<script>`` tags when Django's
   ``ContentSecurityPolicyMiddleware`` is used (Django 6.0+); previously a
   nonce-based policy blocked them and no hits were counted
 * ``HitAdmin.get_actions()`` accepts Django 6.1's ``action_location``
   argument (fixes a ``RemovedInDjango70Warning``)
 * Allow IPv6 addresses `#123`_
 * Django 4+ migration for ``HitCount.content_type`` `#133`_
 * Explicit ``BigAutoField`` primary keys to silence ``models.W042`` `#131`_
 * Chinese translation, and a translatable app verbose name `#137`_
 * Python 3.11 test fixes `#139`_

**Project**

 * Packaging moved to ``pyproject.toml`` (hatchling); ``setup.py``, ``setup.cfg``,
   ``MANIFEST.in`` and the ``requirements.txt`` files were removed
 * CI moved from Travis CI to GitHub Actions (tox matrix, headless-browser
   tests, build check); linting moved from flake8 to ruff
 * The test-suite no longer depends on the name of the checkout directory,
   gained tests for ``get_ip()``, ``insert_hit_count_js``, CSRF-enforced
   end-to-end requests and missing migrations
 * Example project updated to current Django (``path()`` routes, a
   dependency-free ``insert_hit_count_js`` demo page)

Version 1.3.5
-------------

 * Django 3.x support `#108`_
 * Dropped support for Django < 2.2

Version 1.3.3
-------------

 * Dropped support for Python 2.x `#98`_
 * Make it possible to customize ``HitCount`` model per project `#98`_
 * ``order_by("hit_count_generic__hits")`` gives ``django.db.utils.ProgrammingError`` `#90`_
 * Version 1.3.1 migrate error `#80`_

Version 1.3.2
-------------

 * Drop ``python_2_unicode_compatible`` `#86`_

Version 1.3.1
-------------

 * fixed ValueError: invalid literal for int() with base 10 `#64`_

Version 1.3.0
-------------

 * Django 2.x support (@stasfilin) `#67`_

Version 1.2.4
-------------

 * improved querying speed of `hitcount_cleanup` (@dulacp) `#66`_

Version 1.2.3
-------------

 * added indexing to `Hit.ip` and `Hit.session` (@maxg0) `#63`_
 * removed testing support for python 3.3

Version 1.2.2
-------------

 * added ``on_delete=models.CASCADE`` and test (will be required in version 2.0) `#47`_
 * removed ``b`` (bytes) flag from _initial_ migration `#48`_
 * removed testing support for python 3.2

Version 1.2.1
-------------

 * fixed system check error in Django 1.9 - `#43`_

Version 1.2
-----------

 * added ``hitcount.models.HitCountMixin`` to provide a reverse lookup property to a model's ``HitCount``
 * deprecated ``hitcount.views_update_hit_count()`` and moved the business logic into ``hitcount.views.HitCountMixin.hit_count()``
 * deprecated ``hitcount.views.update_hit_count_ajax()`` and replaced with class-based view ``hitcount.views.HitCountJSONView``
 * deprecated ``static/hitcount-jquery.js`` and replaced with ``static/jquery.postcsrf.js`` (a more generic way to handle the Ajax POST CSRF fun-party)
 * updated Django and Python version testing/support (>=1.7 as of Oct 2015)
 * updated example_project to use new views and jQuery plugin
 * updated tests to rely on the example_project

Version 1.1.1
-------------

 * fixed ``session_key`` returning ``None`` - `#40`_ (>=1.8.4)
 * removed requirement for `SESSION_SAVE_EVERY_REQUEST`
 * removed `patterns` for urls.py (>=1.9)
 * updated management command, using ``BaseCommand`` instead of ``NoArgsCommand`` (>=1.9)
 * added ``TEMPLATES`` to `conftest.py`

Version 1.1.0
-------------

 * added tests (lots of them)
 * added documentation
 * support for Django 1.4.x - 1.8.x
 * support for Python 3.x
 * created an example project
 * squashed bugs
 * released to pip
 * more, I'm sure!

.. note:: if you are upgrading from version 0.2 (it's so old!) the ``HitCount.object_pk`` was changed from a ``CharField`` to a ``PositiveIntegerField``.  You will have to manually fix this in your database after upgrading.

.. _#139: https://github.com/thornomad/django-hitcount/pull/139
.. _#137: https://github.com/thornomad/django-hitcount/pull/137
.. _#133: https://github.com/thornomad/django-hitcount/pull/133
.. _#131: https://github.com/thornomad/django-hitcount/pull/131
.. _#123: https://github.com/thornomad/django-hitcount/pull/123
.. _#108: https://github.com/thornomad/django-hitcount/issues/108
.. _#98: https://github.com/thornomad/django-hitcount/pull/98
.. _#90: https://github.com/thornomad/django-hitcount/issues/90
.. _#80: https://github.com/thornomad/django-hitcount/issues/80
.. _#86: https://github.com/thornomad/django-hitcount/issues/86
.. _#64: https://github.com/thornomad/django-hitcount/issues/64
.. _#67: https://github.com/thornomad/django-hitcount/pull/67
.. _#63: https://github.com/thornomad/django-hitcount/issues/63
.. _#40: https://github.com/thornomad/django-hitcount/issues/40
.. _#43: https://github.com/thornomad/django-hitcount/issues/43
.. _#47: https://github.com/thornomad/django-hitcount/issues/47
.. _#48: https://github.com/thornomad/django-hitcount/pull/48
.. _#66: https://github.com/thornomad/django-hitcount/pull/66
