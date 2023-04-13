import logging
import threading
import os

from skpy import Skype, SkypeAuthException

from translator.translators.Translator import Translator
from translator.translators.skype.SkypeListener import SkypeListener
from translator.translators.skype.utils import getChatFromMessage

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)

class SkypeTranslator(Translator):

    socialID="skype"
    _thread = None

    def __init__(self, user, listen=False):
        self._user = user
        self._token = os.path.join(dir, "sessions", user)
        self._listener = None
        self._listen = listen
        try:
            self._client = Skype(tokenFile=self._token)
            self.createListener()
        except:
            self._client = Skype(connect=False)

    def configure(self, data):
        if self.isConnected():
            return {'detail': "successful configuration", 'code' : self.SUCCESS_CODE}

        if data.get('auth_code') is not None and self._user is not None:
            try:
                self._client = Skype(self._user, data['auth_code'], self._token)
            except SkypeAuthException:
                return {'detail': "failed provided code. Check it and try again", 'code': self.ERROR_CODE}

            if self.isConnected():
                return {'detail': "successful configuration", 'code': self.SUCCESS_CODE}

        if data.get('username') is None:
            return {'detail': "missing username for configuration process", 'code': self.ERROR_CODE}

        return {'detail': "add password for a successfull configuration", 'code': self.MORE_INFO_CODE}


    def isConnected(self):
        if self._client.conn.connected:
            self.createListener()
            return True
        if self._token is not None and self._user is not None:
            self._client.conn.setTokenFile(self._token)
            try:
                self._client.conn.readToken()
            except (SkypeAuthException, FileNotFoundError) as e:
                return False

            if self._client.conn.connected:
                self.createListener()
                return True
        return False


    def sendText(self, message):
        chat = getChatFromMessage(self._client, message)
        if type(chat) is dict:
            return chat

        msg = chat.sendMsg(message.content)

        if msg is None:
            return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}


    def sendImage(self, message):
        return self.sendFile(message, image=True)

    def sendVideo(self, message):
        return self.sendFile(message)

    def sendAudio(self, message):
        return self.sendFile(message)

    def sendFile(self, message, image=False):
        chat = getChatFromMessage(self._client, message)
        if type(chat) is dict:
            return chat

        textMsg = None
        if message.content is not None:
            textMsg = chat.sendMsg(message.content)
        mediaMsg = chat.sendFile(open(message.file.path, 'rb'), os.path.basename(message.file.path), image)

        if mediaMsg is None or (message.content is not None and textMsg is None):
            return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}


    def createListener(self):
        if not self._listen or self._listener is not None:
            return
        self._listener = SkypeListener(tokenFile=self._token, autoAck=False)
        self._listener.user = self._user
        self._listener.translator = self
        self.runListener()


    def runListener(self):
        logger.info("Running listener for user {} in social network {}".format(self._user, self.socialID))
        self._thread = threading.Thread(target=self._listener.loop, args=())
        self._thread.daemon = True
        self._thread.start()
