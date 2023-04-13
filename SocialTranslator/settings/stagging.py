from .default import *

BASE_URL = "https://guarded-retreat-96811.herokuapp.com"

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'guarded-retreat-96811.herokuapp.com']

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

FAMILY_API_URL = "https://socialconnector.dcc.uchile.cl/api/"
FAMILY_API_USER = "socialtranslator"
FAMILY_API_PASSWORD = "server123"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
