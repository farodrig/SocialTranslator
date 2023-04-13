import json
import logging
import os

from telethon import TelegramClient, events
from telethon.errors import PhoneCodeInvalidError
from telethon.tl.types import UpdateShortMessage, UpdateNewMessage

from translator.translators.Translator import Translator
from translator.translators.telegram.utils import upload_progress_callback, \
    createMessage
from translator.translators.utils import getUsernameFromMessage, saveIncomingMessage

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)
out = open(os.path.join(dir, "settings.json")).read()
settings = json.loads(out)

class TelegramTranslator(Translator):

    socialID = "telegram"

    def __init__(self, user, listen = False):
        self._client = TelegramClient(os.path.join(dir, "sessions", user), settings['api_id'], settings['api_hash'], update_workers=4)
        self._client.connect()
        if listen:
            self._client.add_event_handler(self.messageReceiver, events.NewMessage(incoming=True))


    def configure(self, data):
        if self._client.is_user_authorized():
            return {'detail': "successful configuration", 'code' : self.SUCCESS_CODE}

        if data.get('auth_code') is not None:
            try:
                self._client.sign_in(code = data['auth_code'])
            except ValueError:
                return {'detail': "Configuration just with username must be called first", 'code': self.ERROR_CODE}
            except PhoneCodeInvalidError:
                return {'detail': "Invalid phonecode. Retry", 'code': self.ERROR_CODE}

            if self._client.is_user_authorized():
                return {'detail': "successful configuration", 'code': self.SUCCESS_CODE}
            return {'detail': "Provided access number for configuration process is invalid", 'code': self.ERROR_CODE}

        if data.get('username') is None:
            return {'detail': "missing user's number for configuration process", 'code': self.ERROR_CODE}

        self._client.sign_in(data['username']) #username must be phone number
        return {'detail': "add code verificator for a successfull configuration", 'code': self.MORE_INFO_CODE}


    def isConnected(self):
        if not self._client.is_connected():
            self._client.connect()
        if not self._client.is_user_authorized():
            msg = "The user in telegram should be preauthorized"
            logger.info(ConnectionError(msg))
            return False
        return True

    def sendText(self, message):
        if not self.isConnected():
            return {'detail': "user is not connected, try configure", 'code': self.ERROR_CODE}

        fromUser, toUser = getUsernameFromMessage(message)

        entity = self._client.get_entity(toUser)
        msg = self._client.send_message(entity, message.content)
        if msg is None:
            return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}

    def sendImage(self, message):
        return self.sendFile(message)

    def sendVideo(self, message):
        return self.sendFile(message)

    def sendAudio(self, message):
        return self.sendFile(message, voice_note=())

    def sendFile(self, message, force_doc=False, voice_note=None):
        fromUser, toUser = getUsernameFromMessage(message)

        if not self.isConnected():
            return {'detail': "user is not connected, try configure", 'code': self.ERROR_CODE}

        entity = self._client.get_entity(toUser)
        caption = message.content if message.content is not None else ""
        self._client.send_file(entity, message.file.path, caption=caption, progress_callback=upload_progress_callback,
                               force_document=force_doc, is_voice_note=voice_note)
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}

    @staticmethod
    def messageReceiver(update):
        saveIncomingMessage(createMessage(update.client, update, TelegramTranslator.socialID))
