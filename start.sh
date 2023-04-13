#!/bin/bash
if [ -z "$1" ]
then
      echo "Using enviroment or develop by default"
else
      export DJANGO_SETTINGS_MODULE=SocialTranslator.settings.$1
fi
# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn SocialTranslator.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
