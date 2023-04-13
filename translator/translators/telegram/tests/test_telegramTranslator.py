from datetime import datetime

from django.test import TestCase

from translator.models import HasSocialNetwork
from translator.translators.telegram.TelegramTranslator import TelegramTranslator
from translator.translators.telegram.utils import createMessage
from translator.translators.tests.AbstractTranslatorTest import AbstractTranslatorTest
from translator.translators.utils import objectview


class TestTelegramTranslator(AbstractTranslatorTest, TestCase):

    def setUp(self):
        AbstractTranslatorTest.setUp(self)
        self.receiver_SNID = self.receiver.username

    def getTranslator(self):
        return TelegramTranslator

    def testCreateMessage(self):
        user = "nietoTest"
        from_sn = HasSocialNetwork.objects.filter(social__shortName=TelegramTranslator.socialID,
                                                      user__username=user).first()
        fromUser = TelegramTranslator(from_sn.username, False)

        data = {
            "date": datetime.now(),
            "user_id": fromUser._client.get_me().id,
            "message": "test Message"
        }

        msg = createMessage(fromUser._client, objectview(data), fromUser.socialID)
        self.assertIsNone(msg)

        msg = createMessage(self.translator._client, objectview(data), self.translator.socialID)
        self.assertIsNotNone(msg)

        data["user_id"] = 1234
        msg = createMessage(self.translator._client, objectview(data), self.translator.socialID)
        self.assertIsNone(msg)