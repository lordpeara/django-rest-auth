"""
Django Rest Framework Auth provides very simple & quick way to adopt
authentication APIs' to your django project.


Rationale
---------

django-rest-framework's `Serializer` is nice idea for detaching
business logic from view functions. It's very similar to django's
``Form``, but serializer is not obligible for rendering response data,
and should not. - django forms also do this, seriously!!!
some expert beginners just know form is ONLY FOR `html form rendering` :(

Unluckily, even though django already provides forms and views
for authentication, We cannot use these for REST-APIs. It uses forms!!
(rest_framework does not use forms.)

We think there should be some serializers & views (or viewsets)
to use ``rest_framework``'s full features.
(such as throttling, pagination, versioning or content-negotiations)

Let's have a good taste of these elegant implementations.
"""

__version__ = '0.1.1dev0'
