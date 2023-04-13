from django.conf.urls import url, include

from . import JWTurls

urlpatterns = [
    url(r'^jwt/', include(JWTurls)),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
