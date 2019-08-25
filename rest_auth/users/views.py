# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordContextMixin,
)
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import (
    sensitive_post_parameters as django_sensitive_post_parameters,
)
from django.views.generic import TemplateView
from rest_framework import viewsets

from .serializers import (
    UserSerializer,
)
from ..views import EmailVerificationMixin

UserModel = get_user_model()


class UserEmailVerificationMixin(EmailVerificationMixin):
    def perform_create(self, serializer):
        email_opts = self.get_email_opts(request=self.request)
        serializer.save(email_opts=email_opts)


class UserViewSet(UserEmailVerificationMixin, viewsets.ModelViewSet):
    """Viewset for UserModel.
    """
    queryset = UserModel._default_manager.all()
    serializer_class = UserSerializer


class EmailVerificationConfirmView(PasswordContextMixin, TemplateView):
    """Email verification view for newly-created User instances.

    After user verified his/her email, users can use his/her full
    features of website.
    """
    template_name = 'registration/verify_email_confirm.html'
    token_generator = default_token_generator
    title = _('Email Verification')

    INTERNAL_VERIFY_URL_TOKEN = 'verification-success'
    INTERNAL_VERIFY_SESSION_TOKEN = '_rest_auth_verify_email_token'

    @method_decorator(django_sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            _session = request.session

            if token == self.INTERNAL_VERIFY_URL_TOKEN:
                session_token = _session.get(
                    self.INTERNAL_VERIFY_SESSION_TOKEN
                )
                if self.token_generator.check_token(self.user, session_token):
                    # If token is valid, show email verification is successful.
                    self.validlink = True
                    _super = super(EmailVerificationConfirmView, self)
                    return _super.dispatch(request, *args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store token in the session and redirect to
                    # the email-verification-success view w/o token.
                    # (For avoiding leaking tokens in HTTP referer)
                    _session[self.INTERNAL_VERIFY_SESSION_TOKEN] = token

                    redir_url = request.path.replace(
                        token, self.INTERNAL_VERIFY_URL_TOKEN
                    )
                    return HttpResponseRedirect(redir_url)

        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        self.set_user_as_verified(self.user)
        _super = super(EmailVerificationConfirmView, self)
        return _super.get(request, *args, **kwargs)

    def set_user_as_verified(self, user):
        user.is_active = True
        user.save(update_fields=['is_active'])

    def get_user(self, uidb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        return user

    def get_context_data(self, **kwargs):
        _super = super(EmailVerificationConfirmView, self)
        context = _super.get_context_data(**kwargs)
        context['validlink'] = self.validlink
        return context
