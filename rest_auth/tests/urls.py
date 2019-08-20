from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('rest_auth.urls', )),
    url(r'^user/', include('rest_auth.users.urls', )),
]
