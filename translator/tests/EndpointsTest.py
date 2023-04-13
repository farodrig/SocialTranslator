import logging

from django.urls import reverse
from rest_framework.test import APITestCase

from translator.models import HasSocialNetwork
from translator.translators.gmail.GmailTranslator import GmailTranslator

logger = logging.getLogger(__name__)

class TestEndpoints(APITestCase):

    def setUp(self):
        self.sender = HasSocialNetwork.objects.filter(social__shortName=GmailTranslator.socialID,
                                                      user__username="farodrig").first()
        self.username = self.sender.alias if self.sender.alias is not None else self.sender.username

    def testAuth(self):
        url = reverse('auth-callback', kwargs={'social':GmailTranslator.socialID})
        logger.debug(url)
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        data['state'] = "asdf"
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        data['code'] = 1234
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        data['state'] = self.username
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)


