# SocialTranslator Documentation

API to allow people and apps to speak with his contacts through different Social Networks. Even if they don't know how to use them.

Currently support Telegram, Gmail and Skype.

The project consist of two different APIs, [Community](api/community.md) and [Translator](api/translator.md). Both are focused on send messages to different social networks but applying different business logic.

### Requirements
  - [Python 3](https://docs.python.org/3/)
  - [pip](https://pip.pypa.io/en/stable/)
  - Other requirements in file "requirements.txt" (must be installed with pip)

### Building

Having python 3 and pip installed. Follow the next steps.

```sh
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata initial-data.json
python manage.py createsuperuser
```

The `python manage.py createsuperuser` is an optional command that could be useful if the database don't have already set a superuser.

### Running

`ENV` is optional ('develop' by default) and should be replaced according to your configuration. It could be 'production' or 'develop'.

```sh
sh start.sh ENV
```

### Limitations

  - Just allows to use Telegram, Skype and Gmail.
  - The login protocols accepted are basic user-password and oauth2.
  - Can send just text, image, audio and video files.