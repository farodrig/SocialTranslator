import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class API():
    URL = settings.COMMUNITY_API_URL
    user = settings.COMMUNITY_API_USER
    pwd = settings.COMMUNITY_API_PASSWORD
    jwt = None

    @classmethod
    def login(cls):
        url = cls.URL + "login/"
        data = {'username': cls.user, 'password': cls.pwd}
        try:
            r = requests.post(url, data=data, timeout=5)
        except Exception as e:
            logger.info("Timeout with CommunityAPI login")
            return
        if r.status_code >= 400:
            logger.error("Error with login. Try again later or ask administrator")
            return
        cls.jwt = r.json()['token']


    @classmethod
    def get(cls, user):
        url = cls.URL + "social/" + user + "/"
        try:
            r = requests.get(url, headers=cls.getJWTHeader(), timeout=5)
        except Exception as e:
            logger.info("Timeout with CommunityAPI get")
            return {}
        if r.status_code == 401:
            cls.login()
            return cls.get(user)
        return r.json()


    @classmethod
    def getAll(cls):
        url = cls.URL + "social/all/"
        try:
            r = requests.get(url, headers=cls.getJWTHeader(), timeout=5)
        except Exception as e:
            logger.info("Timeout with CommunityAPI getAll")
            return []
        if r.status_code == 401:
            cls.login()
            return cls.getAll()
        try:
            return r.json()
        except Exception as e:
            logger.error(e)
            return []

    @classmethod
    def postPreferences(cls, user, data):
        url = cls.URL + "social/" + user + "/"
        try:
            r = requests.post(url, headers=cls.getJWTHeader(), json=data, timeout=5)
        except Exception as e:
            logger.info("Timeout with CommunityAPI postPreferences")
            return []
        if r.status_code == 401:
            cls.login()
            return cls.postPreferences(user, data)
        return r.status_code < 400

    @classmethod
    def getJWTHeader(cls):
        JWT = cls.jwt if cls.jwt is not None else ""
        return {'Authorization': 'JWT ' + JWT}