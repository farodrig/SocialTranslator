from django.conf import settings
from django.conf.urls import include
from django.contrib import admin

from translator import urls as translatorURLs
from community import urls as communityURLs
from auth import urls as authURLs
from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Social Translator API')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^translator/', include(translatorURLs)),
    url(r'^community/', include(communityURLs)),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', schema_view),
    url(r'^auth/', include(authURLs))
] \
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)