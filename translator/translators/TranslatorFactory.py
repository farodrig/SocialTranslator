import logging

from translator.models import HasSocialNetwork
from .skype.SkypeTranslator import SkypeTranslator
from .telegram.TelegramTranslator import TelegramTranslator
from .gmail.GmailTranslator import GmailTranslator
from .whatsapp.WhatsappTranslator import WhatsappTranslator

logger = logging.getLogger(__name__)

class TranslatorFactory:

    translators = {}

    @classmethod
    def build(cls, sender: HasSocialNetwork):
        if cls.getTranslator(sender.pk) != None:
            logger.info("reusing translator")
            return cls.translators[sender.pk]
        kind = sender.social.pk
        username = sender.alias if sender.alias is not None else sender.username
        translator = None
        listen = sender.user.profile is not None and sender.user.profile.requires_assistant
        if kind=="telegram" :
            translator = TelegramTranslator(username, listen)
        elif kind == "gmail":
            translator = GmailTranslator(username, listen)
        elif kind == "skype":
            translator = SkypeTranslator(sender.username, listen)
        elif kind == "whatsapp":
            translator = WhatsappTranslator(sender.username, listen)
        if translator is not None:
            cls.translators[sender.pk] = translator
            return translator

        logger.error(ValueError("{} is not supported".format(kind)))
        return None

    @classmethod
    def getPushHandler(cls, social):
        kind = social.pk
        if (kind=="gmail"):
            return GmailTranslator.pushHandler
        raise ValueError("{} is not supported".format(kind))

    @classmethod
    def getTranslator(cls, has_social):
        if has_social in cls.translators:
            return cls.translators[has_social]
        return None
