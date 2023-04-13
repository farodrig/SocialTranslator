from django.test import TestCase

from translator.translators.gmail.GmailTranslator import GmailTranslator
from translator.translators.tests.AbstractTranslatorTest import AbstractTranslatorTest


class TestGmailTranslator(AbstractTranslatorTest, TestCase):

    def getTranslator(self):
        return GmailTranslator

    def testpushHandler(self):
        data = {
            "message": {
                "data": "eyJlbWFpbEFkZHJlc3MiOiAiZmFyb2RyaWc5MkBnbWFpbC5jb20iLCAiaGlzdG9yeUlkIjogIjE4Mjk4NTIifQ==",
                "message_id": "1234567890"
            },
            "subscription": "projects/pacific-card-187718/subscriptions/social-translator-gmail"
        }
        self.assertEqual(GmailTranslator.pushHandler(data)['status'], GmailTranslator.SUCCESS_CODE)
        data["message"]["data"] = "eyJlbWFpbEFkZHJlc3MiOiAiZmFrZUBmYWtlLmNvbSIsICJoaXN0b3J5SWQiOiAiMTgyOTg1MiJ9"
        self.assertEqual(GmailTranslator.pushHandler(data)['status'], GmailTranslator.ERROR_CODE)

    def testMessageReceiver(self):
        self.assertIsNone(self.translator.messageReceiver(-1))
        self.assertEqual(0, self.translator.messageReceiver(str(int(self.translator._last_hist_id) + 1)))

    def testSaveIncomingMessage(self):
        msg = {
            "id": 123,
            "from": "test",
            "to": "test",
            "content": "contenido de prueba",
            "subject": "subject",
            "date": "Mon, 20 Nov 1995 19:12:08 -0500"
        }

        self.assertIsNone(self.translator._saveIncomingMessage(msg))

        msg["from"] = self.sender_SNID
        self.assertIsNone(self.translator._saveIncomingMessage(msg))

        msg["to"] = self.receiver_SNID
        #self.assertRaises(AttributeError, self.translator._saveIncomingMessage, msg)
        self.assertEqual(self.translator._saveIncomingMessage(msg), 1)