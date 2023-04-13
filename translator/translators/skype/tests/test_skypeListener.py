import os
from datetime import datetime
from tempfile import NamedTemporaryFile

from django.test import TestCase
from django.conf import settings as django_settings

from translator.translators.skype.SkypeListener import SkypeListener
from translator.translators.skype.SkypeTranslator import SkypeTranslator
from translator.translators.tests.AbstractTranslatorTest import AbstractTranslatorTest
from translator.translators.utils import objectview


class TestSkypeListener(AbstractTranslatorTest, TestCase):

    def getTranslator(self):
        return SkypeTranslator

    def testCreateMessage(self):
        data = {
            "msg": objectview({
                "time": datetime.now(),
                "userId": "coordinadortestst@gmail.com",
                "plain": "test Listener message creation",
                "file": objectview({
                    "name": None
                }),
                "fileContent": None
            })
        }

        self.assertTrue(isinstance(self.translator._listener, SkypeListener))
        msg = self.translator._listener._saveMessage(objectview(data))
        self.assertIsNotNone(msg)

        data["msg"].file.name = "audio.mp3"
        path = os.path.join(django_settings.BASE_DIR, "media", "test", data["msg"].file.name)
        tf = NamedTemporaryFile(delete=True)
        tf.write(open(path, "rb").read())
        tf.seek(0)
        tf.name = data["msg"].file.name
        data["msg"].fileContent = tf
        msg = self.translator._listener._saveMessage(objectview(data))
        self.assertIsNotNone(msg)

        data["msg"].userId = 1234
        msg = self.translator._listener._saveMessage(objectview(data))
        self.assertIsNone(msg)

        data["msg"].userId = None
        msg = self.translator._listener._saveMessage(objectview(data))
        self.assertIsNone(msg)
