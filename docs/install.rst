Installation
============


Install package

.. code-block:: bash

    $ pip install django-rest-framework-auth


Add ``rest_framework`` to ``INSTALLED_APPS`` in settings.py

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'rest_auth',
        'rest_framework',
        # required by 3 apps, auth, contenttypes and sessions.
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',

        # NOTE place `rest_auth` upper than `django.contrib.admin` if
        # you wanted to adopt email templates `rest_auth` have.
        # (or you see admin's templates)
        # You can ignore that if you write your own email template.
        # (also you should place your own app upper.)
        'django.contrib.admin',
        # And also you should add `django.contrib.staticfiles` to see
        # rest_framework's templates from HTMLRenderers
        'django.contrib.staticfiles',
        # ...
    )


Add ``rest_auth.urls`` to your ``urls.py``

.. code-block:: python

    urlpatterns = [
        url(r'^auth/', include(('rest_auth.urls'))),
    ]
