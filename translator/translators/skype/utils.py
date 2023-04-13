import logging

from skpy import SkypeApiException

from translator.models import HasSocialNetwork

logger = logging.getLogger(__name__)

def getUserFromSkypeUser(user):
    from translator.translators.skype.SkypeTranslator import SkypeTranslator

    has_social = None
    if user is not None:
        has_socials = HasSocialNetwork.objects.filter(username=user, social=SkypeTranslator.socialID)
        if len(has_socials) > 0:
            has_social = has_socials[0]
    if has_social is None:
        has_socials = HasSocialNetwork.objects.filter(alias=user, social=SkypeTranslator.socialID)
        if len(has_socials) > 0:
            has_social = has_socials[0]
    return has_social


def getChatFromMessage(client, message):
    from translator.translators.skype.SkypeTranslator import SkypeTranslator

    if not client.conn.connected:
        return {'detail': "user is not connected, try configure", 'code': SkypeTranslator.ERROR_CODE}

    fromUser, toUser = getSkypeIdFromMessage(client, message)
    if toUser is None:
        return {'detail': "message couldn't be sended because toUser skype ID can't be founded",
                'code': SkypeTranslator.ERROR_CODE}

    chat = getChatFromUser(client, toUser)
    if chat is None:
        return {'detail': "message couldn't be sended because chat can't be founded", 'code': SkypeTranslator.ERROR_CODE}
    return chat

def getChatFromUser(client, user):
    chat = None
    try:
        chat = client.contacts[user].chat
    except SkypeApiException:
        client.contacts[user].invite("Saludos, quiero empezar a chatear contigo")
        try:
            chat = client.contacts[user].chat
        except SkypeApiException as e:
            logger.error(e)
    return chat


def getSkypeIdFromMessage(client, message):
    from translator.translators.utils import getAliasFromMessage, getUsernameFromMessage

    fromUser, toUser = getAliasFromMessage(message)
    if toUser is None:
        fromUser, toUser = getUsernameFromMessage(message)
        toUser = client.contacts.search(toUser)[0].id
    return fromUser, toUser
