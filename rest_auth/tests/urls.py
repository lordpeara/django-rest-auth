from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('rest_auth.urls', namespace='auth')),
    url(r'^user/', include('rest_auth.users.urls', namespace='auth_user')),
]
