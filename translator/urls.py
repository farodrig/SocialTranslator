from django.conf.urls import url
from .views import sendMessage, configure, authCallback, pushNotification

urlpatterns = [
    url(r'^sendMessage/$', sendMessage),
    url(r'^configure/$', configure),
    url(r'^auth/(?P<social>\w+)/$', authCallback, name='auth-callback'),
    url(r'^push-notif/(?P<social>\w+)/$', pushNotification, name='push-notification'),
]
