from django.conf.urls import include, url

from . import routers
from .views import EmailVerificationConfirmView


app_name = 'rest_auth.users'

urlpatterns = [
    url(r'^', include(routers.router.urls)),
    url(r'^v/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        EmailVerificationConfirmView.as_view(), name='verify_email_confirm'),
]
