import base64
import email
import httplib2
import json
import logging
import os

from apiclient import discovery

from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from SocialTranslator.settings import BASE_URL

from oauth2client import client
from oauth2client.file import Storage
from oauth2client.client import HttpAccessTokenRefreshError

from translator.translators.gmail.utils import getLastHistoryId, getListHistory, getMessagesFromHistories, \
    create_message, getBodyFromMessage, getAttachments
from translator.translators.Translator import Translator
from translator.models import HasSocialNetwork, Message
from translator.translators.gmail import utils

dir = os.path.dirname(os.path.realpath(__file__))
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
APPLICATION_NAME = 'SocialTranslator'
logger = logging.getLogger(__name__)

class GmailTranslator(Translator):

    socialID = 'gmail'
    labels = ['UNREAD', 'CATEGORY_PERSONAL', 'INBOX']
    _user = None
    _credentials = None
    _flow = None
    _service = None
    _last_hist_id = '0'
    _listen = None
    _listening = False

    def __init__(self, user, listen = False):
        self._user = user
        self._listen = listen
        self.credential_path = os.path.join(dir, 'credentials', self._user + '.json')
        if os.path.isfile(self.credential_path):
            store = Storage(self.credential_path)
            self._credentials = store.get()
        self._setService()
        if listen and self._service:
            self.startListening()

    def _setService(self):
        if self._service is not None or self._credentials is None:
            return
        http = self._credentials.authorize(httplib2.Http())
        self._service = discovery.build('gmail', 'v1', http=http)
        if self._service is not None:
            try:
                self._last_hist_id = getLastHistoryId(self._service, self._user)
            except HttpAccessTokenRefreshError as error:
                os.remove(self.credential_path)
                store = Storage(self.credential_path)
                self._credentials = store.get()

    def configure(self, data):
        if self._credentials is not None and not self._credentials.invalid:
            return {'detail': "successful configuration", 'code' : self.SUCCESS_CODE}

        if data.get('username') is None:
            return {'detail': "Missing user's email for configuration process", 'code': self.ERROR_CODE}

        if self._flow is not None and 'auth_code' in data:
            try:
                self._credentials = self._flow.step2_exchange(data['auth_code'])
            except:
                return {'detail': "failed provided code. Check it and try again", 'code': self.ERROR_CODE}

            if self._credentials is None or self._credentials.invalid:
                return {'detail': "failed provided code. Check it and try again", 'code': self.ERROR_CODE}

            self._setService()
            store = Storage(self.credential_path)
            store.put(self._credentials)

            return {'detail': "successful configuration", 'code': self.SUCCESS_CODE}

        self._flow = client.flow_from_clientsecrets(
            os.path.join(dir, "settings.json"),
            SCOPES,
            redirect_uri=BASE_URL + reverse('auth-callback', args=[self.socialID]))
        self._flow.user_agent = APPLICATION_NAME

        return {'detail': "Go to redirect URL for a successfull configuration",
                'code': self.MORE_INFO_CODE,
                'redirectURL': self._flow.step1_get_authorize_url(state=self._user)}


    def isConnected(self):
        if not self._credentials or self._credentials.invalid:
            self.credential_path = os.path.join(dir, 'credentials', self._user + '.json')
            if os.path.isfile(self.credential_path):
                store = Storage(self.credential_path)
                self._credentials = store.get()
            if not self._credentials or self._credentials.invalid:
                return False
        self._setService()
        if self._service is None:
            return False
        if self._listen and not self._listening:
            self.startListening()
        return True


    def sendText(self, message):
        return self.sendEmail(message)

    def sendImage(self, message):
        return self.sendEmail(message)

    def sendAudio(self, message):
        return self.sendEmail(message)

    def sendVideo(self, message):
        return self.sendEmail(message)

    def sendEmail(self, message):
        if not self.isConnected():
            return {'detail': "Not able to connect with gmail. Call configure before.", 'code': self.ERROR_CODE}
        try:
            msg = create_message(message)
            msg = (self._service.users().messages().send(userId='me', media_body=msg).execute())
        except Exception as error:
            logger.error("An error occurred: {}".format(error))
        else:
            return {'detail': "message sended successfully", 'code': self.SUCCESS_CODE}
        return {'detail': "message couldn't be sended", 'code': self.ERROR_CODE}


    def messageReceiver(self, historyId):
        if int(historyId) <= int(self._last_hist_id):
            return None
        histories = getListHistory(self._service, self._user, self._last_hist_id)
        messages = getMessagesFromHistories(self._service, self._user, histories, labelIds=self.labels,
                                            messages_ids=self.getUnreadedMessages())
        for message in messages:
            self._saveIncomingMessage(message)
        self._last_hist_id = str(historyId)
        return len(messages)

    @classmethod
    def pushHandler(cls, data):
        payload = json.loads(base64.b64decode(data['message']['data']).decode('utf-8'))

        has_social = HasSocialNetwork.objects.filter(username=payload['emailAddress'], social=cls.socialID)
        if len(has_social) != 1:
            return {'detail': "User not founded", 'status' : cls.ERROR_CODE}
        has_social = has_social[0]

        from translator.translators.TranslatorFactory import TranslatorFactory
        translator = TranslatorFactory.build(has_social)

        try:
            translator.messageReceiver(payload['historyId'])
        except Exception as e:
            logger.error(e)
        else:
            return {'detail': "Saves message successfully", 'status' : cls.SUCCESS_CODE}
        return {'detail': "Unable to save the message", 'status' : cls.ERROR_CODE}


    def startListening(self):
        request = {
            'labelIds': self.labels,
            'topicName': 'projects/pacific-card-187718/topics/social-translator-gmail'
        }
        self._last_hist_id = '1'
        try:
            self._last_hist_id = str(self._service.users().watch(userId='me', body=request).execute()['historyId'])
        except:
            logger.info("Unable to watch {}'s inbox".format(self._user)) # TODO cron to refresh watch
        else:
            self._listening = True

    def _saveIncomingMessage(self, msg):
        fromUser, toUser = self.getUsersFromMessage(msg)
        if fromUser is None or toUser is None:
            return None
        content = getBodyFromMessage(msg)
        if "subject" in msg and utils.subject not in msg['subject']:
            content = msg['subject'] + "\r\n" + content

        data = {
            'fromUser': fromUser,
            'toUser': toUser,
            'through': self.socialID,
            'content': content,
            'datetime': timezone.localtime(email.utils.parsedate_to_datetime(msg['date'])),
            'sourceID': msg['id']
        }

        from translator.translators.utils import saveIncomingMessage
        temp_dir = os.path.join(settings.BASE_DIR, "temp")
        processed = 0 if saveIncomingMessage(data) is None else 1
        data['content'] = None
        attachs = getAttachments(self._service, self._user, msg['id'], temp_dir)
        for attach in attachs:
            data['file'] = attach
            saveIncomingMessage(data)

        return len(attachs) + processed


    def getUsersFromMessage(self, msg):
        orig = email.utils.parseaddr(msg['from'])[1].lower()
        dest = email.utils.parseaddr(msg['to'])[1].lower()
        fromUser = HasSocialNetwork.objects.filter(username=orig, social=self.socialID)
        if len(fromUser) != 1:
            return None, None
        fromUser = fromUser[0].user
        toUser = HasSocialNetwork.objects.filter(username=dest, social=self.socialID)
        if len(toUser) != 1:
            return fromUser, None
        toUser = toUser[0].user
        return fromUser, toUser

    def getUnreadedMessages(self):
        try:
            hsn = HasSocialNetwork.objects.get(username=self._user, social__shortName=self.socialID)
            msgs = Message.objects.filter(toUser=hsn.user, through__shortName=self.socialID, kind="input")\
                .exclude(sourceID__isnull=True)
            return list(map((lambda msg: msg.sourceID), msgs))
        except Exception as e:
            logger.error(e)
        return []

