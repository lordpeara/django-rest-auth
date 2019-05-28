from django.conf.urls import url

from .views import (
    LoginView, LogoutView,
    PasswordForgotView, PasswordResetDoneView,
    PasswordForgotConfirmView, PasswordChangeView,
)


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
]
