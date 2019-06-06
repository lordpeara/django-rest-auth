.. django-rest-auth documentation master file, created by sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-rest-framework-auth
==========================

`django-rest-framework-auth <https://github.com/lordpeara/django-rest-auth>`_
is a authentication provider for django and rest_framework.

With very simple instructions, you can add your authentication API.


Quickstart
----------

Just install it, including urls and see APIs from your browsable API.

.. code-block:: bash

    $ pip install rest-framework-auth
    $ django-admin startproject proj
    $ vi proj/proj/settings.py

.. code-block:: python

    # urls.py
    # ...
    urlpatterns += [
        url(r'^auth/', 'rest_auth.urls', name='auth'),
    ]

.. code-block:: bash

    $ python manage.py runserver

see API lists! http://localhost:8000/auth/api-root/


Contents
--------

.. toctree::
   :maxdepth: 2
