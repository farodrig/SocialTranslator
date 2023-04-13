import logging
import os

from translator.models import HasSocialNetwork, Message, SocialNetwork

logger = logging.getLogger(__name__)

def _getHasSNFromMessage(msg):
    if msg is None or msg.fromUser is None or msg.through is None or msg.toUser is None:
        return None, None

    fromUser = None
    if msg.fromUser is not None:
        fromUser = HasSocialNetwork.objects.get(user=msg.fromUser, social=msg.through.pk)

    toUser = None
    if msg.toUser is not None:
        toUser = HasSocialNetwork.objects.get(user=msg.toUser, social=msg.through.pk)

    return fromUser, toUser

def getUsernameFromMessage(msg):
    fromUser, toUser = _getHasSNFromMessage(msg)
    nickFU = fromUser.username if fromUser is not None else None
    nickTU = toUser.username if toUser is not None else None
    return nickFU, nickTU

def getAliasFromMessage(msg):
    fromUser, toUser = _getHasSNFromMessage(msg)
    aliasFU = fromUser.alias if fromUser is not None else None
    aliasTU = toUser.alias if toUser is not None else None
    return aliasFU, aliasTU

def _saveMessage(message, kind):
    from translator.utils import saveInteractionLog
    if message is None:
        return
    #Check fields
    if not ("toUser" in message and "fromUser" in message and "through" in message and
                "datetime" in message and ("content" in message or "file" in message)):
        return None

    #Check content
    if message['through'] is None or message['datetime'] is None or (message['content'] is None and message['file'] is None):
        return None

    #Check logic
    if message['fromUser'] is None or message['toUser'] is None or message['fromUser'] == message['toUser']:
        return None

    #Create message
    msg = Message(fromUser=message['fromUser'], toUser=message['toUser'], through=SocialNetwork.objects.get(pk=message['through']))
    msg.kind = kind
    msg.sourceID = message['sourceID'] if "sourceID" in message else None
    msg.content = message['content'] if "content" in message else None
    if "file" in message:
        msg.file = message['file']
    msg.timestamp = message['datetime']
    msg.save()
    saveInteractionLog(msg)
    try:
        if "file" in message:
            message['file'].close()
            os.remove(message['file'].file.name)
    except Exception as e:
        logger.error(e)
    return msg

def saveOutcomingMessage(message):
    return _saveMessage(message, "output")

def saveIncomingMessage(message):
    return _saveMessage(message, "input")


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d