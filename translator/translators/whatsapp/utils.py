import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from webwhatsapi import WhatsAPIDriver

from webwhatsapi.objects.chat import Chat
from webwhatsapi.objects.message import Message as WhatsappMessage, MediaMessage

from community.utils import shareCommunity
from translator.models import HasSocialNetwork, Message


def isCommunityMember(receiver, chat: Chat) -> bool:

    username = chat.id.get('user', None)
    sender = getUserFromWhatsappUser(username)
    if sender is None:
        return False

    receiver = getUserFromWhatsappUser(receiver)
    if receiver is None:
        return False

    return shareCommunity(sender, receiver)

def getMessageId(msg: WhatsappMessage) -> str:
    user = msg.chat_id.get('user', None)
    if user is None:
        return None
    id = user

    if msg.timestamp is None:
        return id
    id += "-" + str(msg.timestamp)

    if msg.content != 'NOT SUPPORTED CONTENT':
        id += "-" + msg.content[:20]
    elif hasattr(msg, "mime"):
        id += "-" + msg.mime

    return id


def alreadyExistsMessage(msg: WhatsappMessage) -> bool:
    from translator.translators.whatsapp.WhatsappTranslator import WhatsappTranslator

    id = getMessageId(msg)
    messages = Message.objects.filter(through__shortName= WhatsappTranslator.socialID, sourceID=id)

    return len(messages) == 1

def createMessage(client: WhatsAPIDriver, receiver: str, msg: WhatsappMessage) -> dict:
    from translator.translators.whatsapp.WhatsappTranslator import WhatsappTranslator

    message = {}
    message['through'] = WhatsappTranslator.socialID
    message['datetime'] = msg.timestamp

    sender = getUserFromWhatsappUser(msg.chat_id.get('user', None))
    receiver = getUserFromWhatsappUser(receiver)
    if sender is None or receiver is None or sender == receiver:
        return None

    message['fromUser'] = sender
    message['toUser'] = receiver
    message['sourceID'] = getMessageId(msg)

    if isinstance(msg, MediaMessage):
        path = os.path.join(settings.BASE_DIR, "temp", msg.filename.replace("/", ""))
        bytes = client.download_media(msg)
        with open(path, 'wb') as f:
            f.write(bytes.read())
        message['file'] = File(open(path, "rb"))
        message['file'].name = os.path.basename(path)
        message['content'] = None
    else:
        message['content'] = msg.content

    return message

def getUserFromWhatsappUser(username: str) -> User:
    from translator.translators.whatsapp.WhatsappTranslator import WhatsappTranslator

    if username is None:
        return None

    user = HasSocialNetwork.objects.filter(username=username, social__shortName=WhatsappTranslator.socialID)
    if len(user) != 1:
        return None
    return user[0].user

