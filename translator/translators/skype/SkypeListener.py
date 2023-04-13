import os
from django.core.files import File
from django.core.files.base import ContentFile
from skpy import SkypeEventLoop, SkypeNewMessageEvent, SkypeMessageEvent

from translator.models import Message
from translator.translators.skype.utils import getUserFromSkypeUser


class SkypeListener(SkypeEventLoop):

    user = None
    translator = None

    def onEvent(self, event):
        if not (isinstance(event, SkypeMessageEvent)):
            return
        self._saveMessage(event)

    def _saveMessage(self, event):
        from translator.translators.skype.SkypeTranslator import SkypeTranslator

        msg = event.msg
        message = {}
        message['through'] = SkypeTranslator.socialID
        message['datetime'] = msg.time if hasattr(msg, "time") else event.time

        skypeUser = msg.userId
        toUser = self.user
        if skypeUser is None or toUser is None:
            return None
        from_social = getUserFromSkypeUser(skypeUser)
        to_social = getUserFromSkypeUser(toUser)
        if from_social is None or to_social is None or from_social == to_social:
            return None

        if type(event) is SkypeMessageEvent:
            message = Message()
            message.fromUser = to_social.user
            message.toUser = from_social.user
            message.content = "Audio messages for {} are not currently supported " \
                              "by SocialTranslator".format(SkypeTranslator.socialID)
            message.through = from_social.social
            return self.translator.sendText(message)

        message['fromUser'] = from_social.user
        message['toUser'] = to_social.user
        message['content'] = None

        if hasattr(msg, "file") and msg.file is not None and msg.file.name is not None:
            message['file'] = ContentFile(msg.fileContent)
            message['file'].name = msg.file.name
        else:
            message['content'] = msg.plain

        from translator.translators.utils import saveIncomingMessage
        saveIncomingMessage(message)
        return message

