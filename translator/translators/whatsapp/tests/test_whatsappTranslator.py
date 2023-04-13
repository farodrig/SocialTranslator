import os

from django.contrib.auth.models import User
from django.test import TestCase
from webwhatsapi.wapi_js_wrapper import JsException

from translator.models import Message
from translator.translators.tests.AbstractTranslatorTest import AbstractTranslatorTest
from translator.translators.whatsapp.WhatsappTranslator import WhatsappTranslator


class TestWhatsappTranslator(AbstractTranslatorTest, TestCase):

    def getTranslator(self):
        return WhatsappTranslator

    def testSendText(self):
        AbstractTranslatorTest.testSendText(self)
        self.assertEqual(self.translator.sendText(None)["code"], WhatsappTranslator.ERROR_CODE)

        msg = Message(
            fromUser=self.sender.user,
            toUser=User.objects.filter(username="nietoTest").first(),
            through=self.social,
            content="Test message"
        )
        self.assertRaises(JsException, self.translator.sendText, msg)


    def testSendImage(self):
        AbstractTranslatorTest.testSendImage(self)
        self.assertEqual(self.translator.sendImage(None)["code"], WhatsappTranslator.ERROR_CODE)