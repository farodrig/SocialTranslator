# SocialTranslator

API to allow people and apps to speak with his contacts through different Social Networks. Even if they don't know how to use them. 

Actually support Telegram, Gmail and Skype.

### Requirements
  - [Python 3](https://docs.python.org/3/)
  - [pip](https://pip.pypa.io/en/stable/)
  - Other requirements in file "requirements.txt" (must be installed with pip)

### Building

Having python 3 and pip installed. Follow the next steps.

```sh
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata initial-data.json socialNetworks users hasSocialNetworks community userProfiles
python manage.py createsuperuser `#OPTIONAL`
```

The `python manage.py createsuperuser` command could be useful if the database don't have already set a superuser.

### Running

`ENV` is optional ('develop' by default) and should be replaced according to your configuration. It could be 'production' or 'develop'.

```sh
sh start.sh ENV
```

### Cron Tasks

`django manage.py updatepreferences` It updates the user preferences using the interaction log. Must run after the same number of forecasted days in settings.PREFERENCES_FORECAST.

`django manage.py pulluserdata` It download the userdata from SocialConnector.


### More Docs

For more documentation please go to the [docs](https://farodrig.github.io/SocialTranslator/).

### Limitations

  - Just allows to use Telegram, Skype and Gmail.
  - The login protocols accepted are basic user-password and oauth2.
  - Can send just text, image, audio and video files.
