from collections import OrderedDict

from django.conf import settings
from django.conf.urls import url
from rest_framework.routers import APIRootView

from .views import (
    EmailVerificationConfirmView, LoginView, LogoutView,
    PasswordChangeView, PasswordForgotConfirmView,
    PasswordForgotView, PasswordResetDoneView,
    SignupView,
)


app_name = 'rest_auth'

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^forgot/$', PasswordForgotView.as_view(), name='forgot'),

    url(r'^reset/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordForgotConfirmView.as_view(), name='password_reset_confirm'),

    url(r'^reset/d/$',
        PasswordResetDoneView.as_view(),
        name='password_reset_complete'),

    url(r'^change-password/$',
        PasswordChangeView.as_view(),
        name='password_change'),

    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^signup/v/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        EmailVerificationConfirmView.as_view(), name='verify_email_confirm'),
]


if settings.REST_AUTH_API_ROOT_VIEW:
    api_root = OrderedDict()
    for pattern in urlpatterns:
        api_root[pattern.name] = pattern.name

    urlpatterns += [
        url(r'^$',
            APIRootView.as_view(api_root_dict=api_root), name='api-root'),
    ]
