import os
import time

from abc import ABC, abstractmethod

from django.core.files import File
from django.conf import settings

from translator.models import HasSocialNetwork, SocialNetwork, Message
from translator.translators.Translator import Translator
from translator.translators.TranslatorFactory import TranslatorFactory


class AbstractTranslatorTest(ABC):
    fixtures = ["socialNetworks", "community", "userProfiles", "users", "hasSocialNetworks" ]
    translator = None
    sender: HasSocialNetwork = None
    sender_SNID: str = None
    receiver: HasSocialNetwork = None
    receiver_SNID: str = None

    def setUp(self):
        receiver_username = "coordinadorTest"
        self.receiver = HasSocialNetwork.objects.filter(social__shortName=self.getTranslator().socialID,
                                                      user__username=receiver_username).first()
        self.receiver_SNID = self.receiver.alias if self.receiver.alias is not None else self.receiver.username

        sender_username = "abueloTest"
        self.sender = HasSocialNetwork.objects.filter(social__shortName=self.getTranslator().socialID,
                                                      user__username=sender_username).first()
        self.sender_SNID = self.sender.alias if self.sender.alias is not None else self.sender.username

        self.translator = TranslatorFactory.build(self.sender)

        self.social = SocialNetwork.objects.get(shortName=self.translator.socialID)

    @abstractmethod
    def getTranslator(self) -> Translator:
        pass

    def testConfigure(self):
        t = self.getTranslator()(self.receiver_SNID, False)
        self.assertEqual(t.configure({})['code'], self.getTranslator().ERROR_CODE)

        data = {"username": self.receiver_SNID}
        self.assertEqual(t.configure(data)['code'], self.getTranslator().MORE_INFO_CODE)
        self.assertEqual(self.translator.configure(data)['code'], self.getTranslator().SUCCESS_CODE)

        data["auth_code"] = "12345"
        self.assertEqual(t.configure(data)['code'], self.getTranslator().ERROR_CODE)

    def testIsConnected(self):
        t = self.getTranslator()(self.receiver_SNID, False)
        self.assertFalse(t.isConnected())
        self.assertTrue(self.translator.isConnected())

    def testSendText(self):
        self.sendMessage("text")

    def testSendAudio(self):
        self.sendMessage("audio", "audio.mp3")

    def testSendImage(self):
        self.sendMessage("image", "image.jpg")

    def testSendVideo(self):
        self.sendMessage("video", "video.mp4")

    def sendMessage(self, type, file=None):
        t = self.getTranslator()(self.receiver_SNID, False)

        msg = Message(
            fromUser=self.sender.user,
            toUser=self.receiver.user,
            through=self.social,
            content="Test message"
        )

        if file is not None:
            path = os.path.join(settings.BASE_DIR, "media", "test", file)
            msg.file = File(open(path, "rb"))
            msg.file.name = os.path.basename(path)
        msg.save()

        if type == "video":
            fun1 = t.sendVideo
            fun2 = self.translator.sendVideo
        elif type == "image":
            fun1 = t.sendImage
            fun2 = self.translator.sendImage
        elif type == "audio":
            fun1 = t.sendAudio
            fun2 = self.translator.sendAudio
        else:
            fun1 = t.sendText
            fun2 = self.translator.sendText

        sendFun = t.getSendFunction(msg)
        self.assertEqual(sendFun, fun1)
        self.assertEqual(sendFun(msg)['code'], self.getTranslator().ERROR_CODE)

        sendFun = self.translator.getSendFunction(msg)
        self.assertEqual(sendFun, fun2)
        self.assertEqual(sendFun(msg)['code'], self.getTranslator().SUCCESS_CODE)
