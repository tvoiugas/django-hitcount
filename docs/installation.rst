Installation and Usage
======================

Install django-hitcount::

    pip install django-hitcount

Add django-hitcount to your ``INSTALLED_APPS``::

    # settings.py
    INSTALLED_APPS = [
        ...
        'hitcount',
    ]

Perform database migration::

    python manage.py migrate

View the :doc:`additional settings section </settings>` for a list of the django-hitcount settings that are available.

For a working implementation, you can view the `example project`_ on Github.

Counting Hits
-------------

The main business-logic for evaluating and counting a `Hit` is done in ``hitcount.views.HitCountMixin.hit_count()``.  You can use this class method directly in your own Views or you can use one of the Views packaged with this app.

 * `HitCountJSONView`_: a JavaScript implementation which moves the business-logic to an Ajax View and hopefully speeds up page load times and eliminates some bot-traffic
 * `HitCountDetailView`_: which provides a wrapper from  Django's generic ``DetailView`` and allows you to process the Hit as the view is loaded

HitCountMixin
^^^^^^^^^^^^^

This mixin can be used in your own class-based views or you can call the ``hit_count()`` class method directly.   The method takes two arguments, a ``HttpRequest`` and ``HitCount`` object it will return a namedtuple: ``UpdateHitCountResponse(hit_counted=Boolean, hit_message='Message')``.  ``hit_counted`` will be ``True`` if the hit was counted and ``False`` if it was not.  ``hit_message`` will indicate by what means the Hit was either counted or ignored.

It works like this. ::

    from hitcount.models import HitCount
    from hitcount.views import HitCountMixin

    # first get the related HitCount object for your model object
    hit_count = HitCount.objects.get_for_object(your_model_object)

    # next, you can attempt to count a hit and get the response
    # you need to pass it the request object as well
    hit_count_response = HitCountMixin.hit_count(request, hit_count)

    # your response could look like this:
    # UpdateHitCountResponse(hit_counted=True, hit_message='Hit counted: session key')
    # UpdateHitCountResponse(hit_counted=False, hit_message='Not counted: session key has active hit')

To see this in action see the `views`_.py code.

HitCountJSONView
^^^^^^^^^^^^^^^^

The ``hitcount.views.HitCountJSONView`` can be used to handle an AJAX POST request.

If you wish to use the ``HitCountJSONView`` in your project you first need to update your ``urls.py`` file to include the following::

    # urls.py
    from django.urls import include, path

    urlpatterns = [
        ...
        path('hitcount/', include('hitcount.urls', namespace='hitcount')),
    ]

The easiest way to send the request is the ``{% insert_hit_count_js %}`` template tag.  It writes a small, dependency-free ``<script>`` that POSTs the hit with the browser's ``fetch()`` API.  The CSRF token is taken from the template context (falling back to the CSRF cookie), so neither jQuery nor ``@ensure_csrf_cookie`` is needed::

    {% load hitcount_tags %}
    {% insert_hit_count_js for post %}

    {# or, to log the response to the browser console: #}
    {% insert_hit_count_js for post debug %}

When the request finishes, a ``hitcount:counted`` event is dispatched on ``document`` with the ``HitCountJSONView`` response in ``event.detail`` (or ``hitcount:error`` if the request failed).  Register your listener before the tag if you want to react to the result, for example to update the page::

    <script>
    document.addEventListener("hitcount:counted", function (event) {
      document.getElementById("hit-response").textContent = event.detail.hit_message;
    });
    </script>
    {% insert_hit_count_js for post %}

Writing your own JavaScript
"""""""""""""""""""""""""""

If you prefer to write the request yourself, use the ``{% get_hit_count_js_variables for post as [var_name] %}`` template tag to get the ``ajax_url`` and ``pk`` for your object.  The ``pk`` is needed for POST-ing to the ``HitCountJSONView``.  The request must:

* be a ``POST`` with a ``hitcountPK`` form field
* send the ``X-Requested-With: XMLHttpRequest`` header (other requests get a ``404``)
* send the CSRF token in the ``X-CSRFToken`` header

django-hitcount also still ships a small `jQuery plugin`_ that handles the CSRF token for you.  Here is an example taken from the `example project`_; note that the view rendering this template should be decorated with ``@ensure_csrf_cookie`` so that the cookie is set::

    {% load static %}
    <script src="{% static 'hitcount/jquery.postcsrf.js' %}"></script>

    {% load hitcount_tags %}
    {% get_hit_count_js_variables for post as hitcount %}
    <script>
    jQuery(document).ready(function($) {
      // use the template tags in our JavaScript call
      $.postCSRF("{{ hitcount.ajax_url }}", { hitcountPK : "{{ hitcount.pk }}" })
        .done(function(data){
          $('<i />').text(data.hit_counted).attr('id','hit-counted-value').appendTo('#hit-counted');
          $('#hit-response').text(data.hit_message);
      }).fail(function(data){
          console.log('POST failed');
          console.log(data);
      });
    });
    </script>

HitCountDetailView
^^^^^^^^^^^^^^^^^^

The ``HitCountDetailView`` can be used to do the business-logic of counting the hits by setting ``count_hit=True``.  See the `views`_ section for more information about what else is added to the template context with this view.

Here is an example implementation from the `example project`_::

    from hitcount.views import HitCountDetailView

    class PostCountHitDetailView(HitCountDetailView):
        model = Post        # your model goes here
        count_hit = True    # set to True if you want it to try and count the hit

.. note:: Unlike the JavaScript implementation (above), this View will do all the HitCount processing *before* the content is delivered to the user; if you have a large dataset of Hits or exclusions, this could slow down page load times.  It will also be triggered by web crawlers and other bots that may not have otherwise executed the JavaScript.

Displaying Hits
---------------

There are different methods for *displaying* hits:

* `Template Tags`_: provide a robust way to get related counts
* `Views`_: allows you to wrap a class-based view and inject additional context into your template
* :doc:`Models </models>`: can have a generic relation to their respective ``HitCount``

Template Tags
^^^^^^^^^^^^^

For a more granular approach to viewing the hits for a related object you can use the ``get_hit_count`` template tag.

::

    # remember to load the tags first
    {% load hitcount_tags %}

    # Return total hits for an object:
    {% get_hit_count for [object] %}

    # Get total hits for an object as a specified variable:
    {% get_hit_count for [object] as [var] %}

    # Get total hits for an object over a certain time period:
    {% get_hit_count for [object] within ["days=1,minutes=30"] %}

    # Get total hits for an object over a certain time period as a variable:
    {% get_hit_count for [object] within ["days=1,minutes=30"] as [var] %}

Views
^^^^^

The ``hitcount.views.HitCountDetailView`` extends Django's generic ``DetailView`` and injects an additional context variable ``hitcount``.

::

    {# the primary key for the hitcount object #}
    {{ hitcount.pk }}

    {# the total hits for the object #}
    {{ hitcount.total_hits }}

If you have set ``count_hit=True`` (see: `HitCountDetailView`_) two additional variables will be set.

::

    {# whether or not the hit for this request was counted (true/false) #}
    {{ hitcount.hit_counted }}

    {# the message form the UpdateHitCountResponse #}
    {{ hitcount.hit_message }}


.. _jQuery plugin: https://github.com/thornomad/django-hitcount/blob/master/hitcount/static/hitcount/jquery.postcsrf.js

.. _example project: https://github.com/thornomad/django-hitcount/tree/master/example_project

.. _views: https://github.com/thornomad/django-hitcount/blob/master/hitcount/views.py
