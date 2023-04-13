from django.test import TestCase

from translator.translators.skype.SkypeTranslator import SkypeTranslator
from translator.translators.tests.AbstractTranslatorTest import AbstractTranslatorTest


class TestSkypeTranslator(AbstractTranslatorTest, TestCase):

    def getTranslator(self):
        return SkypeTranslator

    def setUp(self):
        AbstractTranslatorTest.setUp(self)
        self.receiver_SNID = self.receiver.username
        self.sender_SNID = self.sender.username

    def testConfigure(self):
        t = SkypeTranslator(self.receiver_SNID)

        self.assertEqual(t.configure({})['code'], SkypeTranslator.ERROR_CODE)

        data = {"username": self.receiver_SNID}
        self.assertEqual(t.configure(data)['code'], SkypeTranslator.MORE_INFO_CODE)

        data["auth_code"] = "12345"
        self.assertEqual(t.configure(data)['code'], SkypeTranslator.ERROR_CODE)

        self.assertEqual(self.translator.configure(data)['code'], SkypeTranslator.ERROR_CODE)

        data = {"username": self.sender_SNID,
                "auth_code": "SocialTranslator123"}
        self.assertEqual(self.translator.configure(data)['code'], SkypeTranslator.SUCCESS_CODE)
        self.assertEqual(self.translator.configure({})['code'], SkypeTranslator.SUCCESS_CODE)