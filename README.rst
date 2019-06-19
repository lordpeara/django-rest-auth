django-rest-framework-auth
==========================

.. image:: https://api.travis-ci.com/lordpeara/django-rest-framework-auth.svg?branch=stable
    :target: https://travis-ci.com/lordpeara/django-rest-framework-auth

.. image:: https://codecov.io/gh/lordpeara/django-rest-framework-auth/branch/stable/graph/badge.svg
    :target: https://codecov.io/gh/lordpeara/django-rest-framework-auth

.. image:: https://readthedocs.org/projects/django-rest-framework-auth/badge/?version=stable
    :target: https://django-rest-framework-auth.readthedocs.io/en/stable/?badge=stable


django-rest-framework-auth is a django & rest_framework application for
providing REST-APIs for authentication w/ very simple instructions.


Quickstart
----------

1. install packages

.. code-block:: bash

    $ pip install django-rest-framework-auth
    $ django-admin startproject proj
    $ vi proj/proj/settings.py


2. add AppConfig and urls to project

.. code-block:: python

    # settings.py
    # ...
    INSTALLED_APPS = (
        # ...
        'rest_auth',
        'rest_framework',
        # ...
    )

    # urls.py
    # ...
    urlpatterns += [
        url(r'^auth/', 'rest_auth.urls', name='auth'),
    ]


Documentation
-------------

`See Documentation <https://django-rest-framework-auth.readthedocs.io>`_
