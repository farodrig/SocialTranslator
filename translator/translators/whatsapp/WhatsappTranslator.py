import base64
import mimetypes
import logging
import os
import threading
import time

from django.conf import settings as django_settings

from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from translator.translators.Translator import Translator
from translator.translators.utils import getUsernameFromMessage, saveIncomingMessage

from urllib.parse import urljoin

from webwhatsapi import WhatsAPIDriver, ChatNotFoundError

from translator.translators.whatsapp.utils import isCommunityMember, alreadyExistsMessage, createMessage

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


class WhatsappTranslator(Translator):
    socialID = "whatsapp"
    QR_FILENAME = "qr.png"

    def __init__(self, user, listen=False):
        self._user = user
        self._profilesDir = os.path.join(dir, "sessions", user)
        if not os.path.isdir(self._profilesDir):
            os.makedirs(self._profilesDir)
        self._screenshotLoc = os.path.join(self.socialID, user)
        self._screenshotDir = os.path.join(django_settings.BASE_DIR, "media", self._screenshotLoc)
        if not os.path.isdir(self._screenshotDir):
            os.makedirs(self._screenshotDir)

        self._client = WhatsAPIDriver(
            username=user,
            headless=True,
            loadstyles=True,
            profile=self._profilesDir)

        if listen:
            self._new_message_thread = threading.Thread(
                name=user,
                target=self.checkForNewMessages)
            self._new_message_thread.daemon = True
            self._new_message_thread.start()

    def isConnected(self):
        logging.info(self._client.get_status())
        if not self._client.is_logged_in():
            return False
        return True

    def configure(self, data):
        if self.isConnected():
            return {'detail': "successful configuration", 'code': self.SUCCESS_CODE}

        if data.get('username') is None:
            return {'detail': "missing user's number for configuration process", 'code': self.ERROR_CODE}

        if data.get('auth_code') is not None:
            return {'detail': "Whatsapp don't use auth_code. You shouldn't provide it", 'code': self.ERROR_CODE}

        try:
            self._client.reload_qr()
            self._client.get_qr(filename=os.path.join(self._screenshotDir, self.QR_FILENAME))
        except NoSuchElementException:
            pass
        except ElementClickInterceptedException:
            self._client.get_qr(filename=os.path.join(self._screenshotDir, self.QR_FILENAME))

        self.asyncWaitForLogin()
        return {'detail': "Scan QR image with your phone. Image link in redirectURL field",
                'code': self.MORE_INFO_CODE,
                'redirectURL': urljoin(django_settings.BASE_URL,
                                       os.path.join("media", self._screenshotLoc, self.QR_FILENAME))}

    def sendText(self, message):
        if not self.isConnected():
            return {'detail': "user is not connected, try configure", 'code': self.ERROR_CODE}

        _, toUser = getUsernameFromMessage(message)
        if toUser is None:
            return {'detail': "Recipient user doesn't exist or doesn't have username (phone number). Check settings",
                    'code': self.ERROR_CODE}

        try:
            chat = self._client.get_chat_from_phone_number(toUser)
            msg = chat.send_message(message.content)
        except ChatNotFoundError:
            try:
                msg = self._client.chat_send_message_to_new(toUser + "@c.us", message.content)
            except:
                return {'detail': "Recipient user isn't a valid contact", 'code': self.ERROR_CODE}

        if msg is None:
            return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}

    def sendImage(self, message):
        return self.sendMedia(message)

    def sendVideo(self, message):
        return self.sendMedia(message)

    def sendAudio(self, message):
        if message.content is not None:
            self.sendText(message)
        return self.sendMedia(message)

    def sendMedia(self, message):
        if not self.isConnected():
            return {'detail': "user is not connected, try configure", 'code': self.ERROR_CODE}

        _, toUser = getUsernameFromMessage(message)
        if toUser is None:
            return {'detail': "Recipient user doesn't exist or doesn't have username (phone number). Check settings",
                    'code': self.ERROR_CODE}

        path = message.file.path
        base64Media = self._getBase64FromMedia(path)
        try:
            chat = self._client.get_chat_from_phone_number(toUser)
            msg = self._client.chat_send_media(
                chat.get_id(),
                base64Media,
                os.path.basename(path),
                message.content)

        except ChatNotFoundError:
            try:
                self._client.chat_send_message_to_new(toUser + "@c.us", message.content)
                chat = self._client.get_chat_from_phone_number(toUser)
                msg = self._client.chat_send_media(chat.get_id(), base64Media, os.path.basename(path), message.content)
            except:
                msg = None

        if msg is None:
            return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}
        return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}

    def _getBase64FromMedia(self, path):
        content_type = mimetypes.guess_type(path)[0]
        with open(path, "rb") as image_file:
            archive = base64.b64encode(image_file.read())
            archive = archive.decode('utf-8')
        return 'data:' + content_type + ';base64,' + archive

    def asyncWaitForLogin(self):
        self._thread = threading.Thread(target=self.waitForLogin, args=())
        self._thread.daemon = True
        self._thread.start()

    def waitForLogin(self):
        logging.debug("waiting for login")
        try:
            self._client.wait_for_login()
        except TimeoutException:
            logging.debug("login failed")
            return
        logging.debug("login successful")
        self._client.mark_default_unread_messages()
        self._client.save_firefox_profile()

    def checkForNewMessages(self):
        while(True):
            if (self.isConnected()):
                msgs = self._client.get_unread()
                for message_group in msgs:
                    if len(message_group.messages) == 0 or not isCommunityMember(self._user, message_group.chat):
                        continue
                    for msg in message_group.messages:
                        if alreadyExistsMessage(msg):
                            continue
                        saveIncomingMessage(createMessage(self._client, self._user, msg))
                    message_group.chat.send_seen()
            time.sleep(django_settings.NEW_MESSAGES_REFRESH_RATE)
