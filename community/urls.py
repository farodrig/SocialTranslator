from django.conf.urls import url
from .views import sendMessage, checkMessages, getMessages, configure, register, checkNetworks

urlpatterns = [
    url(r'^sendMessage/$', sendMessage),
    url(r'^check/messages/$', checkMessages),
    url(r'^getMessages/$', getMessages),
    url(r'^configure/$', configure),
    url(r'^register/communication/$', register),
    url(r'^check/networks/$', checkNetworks),
]
