Overview
========

Django-Hitcount allows you to track the number of hits (views) for a particular object. This isn’t meant to be a full-fledged tracking application or a real analytic tool; it's just a basic hit counter.

How one tracks a "hit" or "view" of a web page is not such a simple thing as it might seem.  That's why folks rely on Google Analytics or similar tools.  It's tough!  This is a simple app with some settings and features that should suit the basic needs of smaller sites.

It comes ready to track hits with a ``HitCountDetailView`` and a ``HitCountJSONView``.  The out-of-the-box JavaScript (``{% insert_hit_count_js %}``) uses the browser's built-in ``fetch()`` and needs no JavaScript library.

Requirements and Compatibility
------------------------------

The 2.x series supports Django 5.2 (LTS), 6.0 and 6.1 on Python 3.10 or newer (Django 6.x itself requires Python 3.12+).  Development of django-hitcount follows Django's `supported versions release schedule`_ and testing for older versions of Django/Python will be removed as time marches on.

.. note:: If you are stuck on an older Django, pin an older release: django-hitcount 1.3.5 for Django 2.2 - 3.2, v1.1.1 for Django 1.4 - 1.6.

.. _supported versions release schedule: https://www.djangoproject.com/download/#supported-versions
