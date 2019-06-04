# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools

from django.conf import settings
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    SuccessURLAllowedHostsMixin,
)
from django.utils.decorators import method_decorator
from rest_framework import (
    generics, permissions, response, status, views,
)

from .contrib.rest_framework.decorators import sensitive_post_parameters
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
)


class LoginMixin(SuccessURLAllowedHostsMixin):
    """Mixin for logging-in
    """
    # TODO return 302 if needed.
    # redirect_url = False
    response_includes_data = False
    serializer_class = LoginSerializer

    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_login(request, serializer.get_user())

        data = self.get_response_data(serializer.data)
        headers = self.get_success_headers(serializer.data)

        return response.Response(
            data, status=status.HTTP_200_OK, headers=headers,
        )

    def perform_login(self, request, user):
        auth_login(request, user)

    def get_response_data(self, data):
        if self.response_includes_data:
            return data
        return None

    def get_success_headers(self, data):
        return {}


class LoginView(LoginMixin, generics.GenericAPIView):
    """LoginView for REST-API.
    """
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        return self.login(request, *args, **kwargs)


class LogoutView(views.APIView):
    """LogoutView for user logout.
    """
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return response.Response(None, status=status.HTTP_200_OK)


class PasswordForgotMixin(object):
    serializer_class = PasswordResetSerializer

    def forgot(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_opts = self.get_email_opts(request=request)
        serializer.save(**email_opts)

        return response.Response(None, status=status.HTTP_200_OK)

    def get_email_opts(self, **opts):
        email_opts = {}
        email_opts.update(getattr(settings, 'REST_AUTH_EMAIL_OPTIONS', {}))
        email_opts.update(opts)

        return email_opts


class PasswordForgotView(PasswordForgotMixin, generics.GenericAPIView):
    """sending password-reset email to user.
    """

    def post(self, request, *args, **kwargs):
        return self.forgot(request, *args, **kwargs)


class PasswordForgotConfirmView(PasswordResetConfirmView):
    """django-rest-auth's password reset confirmation just adopts django's one.
    This idea is under assumption, which password reset confirmation
    should be done, by clicking password-reset-url we sent and moving to
    webpage to change password.
    """


class PasswordResetDoneView(PasswordResetCompleteView):
    """adopts django's password reset complete view.
    """


class PasswordChangeMixin(object):
    serializer_class = PasswordChangeSerializer

    def get_serializer_class(self):
        # HACK `PasswordChangeSerializer` requires `user` as a first param in
        # __init__, so we should bind it to that class for all HTTP methods.
        klass = super(PasswordChangeMixin, self).get_serializer_class()
        return functools.partial(klass, self.request.user)

    def reset(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(None)


class PasswordChangeView(PasswordChangeMixin, generics.GenericAPIView):
    """password change REST-API view.
    """
    permission_classes = (permissions.IsAuthenticated, )

    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        return self.reset(request, *args, **kwargs)
