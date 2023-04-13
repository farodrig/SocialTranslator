import mimetypes
import logging

from django.contrib.auth.models import User

from translator.models import InteractionLog, SocialNetwork, Preference, HasSocialNetwork
from translator.services import connect

logger = logging.getLogger(__name__)

def saveInteractionLog(message, **kargs):
    log = InteractionLog()
    log.fromUser = message.fromUser
    log.toUser = message.toUser
    log.through = message.through
    if "media" in kargs and kargs['media'] is not None:
        log.media = kargs['media']
    elif message.file.name is None and message.content is not None:
        log.media = "text"
    else:
        for kind in InteractionLog.MEDIA_TYPE:
            if hasattr(message.file.file, "content_type"):
                mime = message.file.file.content_type
            else:
                mime = mimetypes.guess_type(message.file.url)[0]
            if kind[0] in mime:
                log.media = kind[0]
                break

    if "started" in kargs and kargs['started'] is not None:
        log.timestamp = kargs['started']
    if "ended" in kargs and kargs['ended'] is not None:
        log.final_timestamp = kargs['ended']
    log.save()


def userChangePreference(sender, receiver, preference):
    sn = SocialNetwork.objects.filter(name__icontains=preference['network']).first()
    if sn is None:
        logger.info("Not founded similar Social Network")
        return None

    pref = Preference.objects.filter(sender = sender, receiver = receiver, through = sn).first()
    if pref is None:
        pref = Preference(sender=sender, receiver=receiver, through=sn)
    pref.priority = preference['order']
    pref.save()
    return pref


def connectAll():
    try:
        users = User.objects.filter(profile__requires_assistant=True)
        for user in users:
            has_socials = HasSocialNetwork.objects.filter(user=user)
            for has_social in has_socials:
                result = connect(has_social)
                if result.status_code < 400:
                    logger.info("Listening incoming messages for user {} in social network: {}".format(user.username,
                                                                                                 has_social.social.name))
                else:
                    logger.info("Unable to listening incoming messages for user {} in social network: {}".format(user.username,
                                                                                                 has_social.social.name))

    except Exception as e:
        logger.error(e)