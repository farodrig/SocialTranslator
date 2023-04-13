import logging
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from translator.models import HasSocialNetwork

logger = logging.getLogger(__name__)

def getUserFromTelegramUser(telegramUser):
    from translator.translators.telegram.TelegramTranslator import TelegramTranslator

    has_social = None
    if telegramUser.phone is not None:
        has_socials = HasSocialNetwork.objects.filter(username="+" + telegramUser.phone, social=TelegramTranslator.socialID)
        if len(has_socials) > 0:
            has_social = has_socials[0]
    if has_social is None and telegramUser.username is not None:
        has_socials = HasSocialNetwork.objects.filter(alias=telegramUser.username, social=TelegramTranslator.socialID)
        if len(has_socials) > 0:
            has_social = has_socials[0]
    if has_social is None and telegramUser.first_name is not None and telegramUser.last_name is not None:
        u = User.objects.filter(first_name__icontains=telegramUser.first_name,
                                last_name__icontains=telegramUser.last_name).first()
        has_socials = HasSocialNetwork.objects.filter(user=u, social=TelegramTranslator.socialID)
        if len(has_socials) > 0:
            has_social = has_socials[0]
    return has_social

def upload_progress_callback(uploaded_bytes, total_bytes):
    progress_callback("Uploaded", uploaded_bytes, total_bytes)

def download_progress_callback(downloaded_bytes, total_bytes):
    progress_callback("Downloaded", downloaded_bytes, total_bytes)

def progress_callback(kind, current_bytes, total_bytes):
    logger.info('{} {} out of {} ({:.2%})'.format(
        kind, bytes_to_string(current_bytes),
        bytes_to_string(total_bytes), current_bytes / total_bytes)
    )

def bytes_to_string(byte_count):
    """Converts a byte count to a string (in KB, MB...)"""
    suffix_index = 0
    while byte_count >= 1024:
        byte_count /= 1024
        suffix_index += 1

    return '{:.2f}{}'.format(
        byte_count, [' bytes', 'KB', 'MB', 'GB', 'TB'][suffix_index]
    )


def createMessage(client, update, socialID):
    message = {}
    message['through'] = socialID
    message['datetime'] = update.date if hasattr(update, "date") else update.message.date
    # stickers, gifs, photo, audio, video, text
    try:
        telegramUser = client.get_entity(update.user_id) \
            if hasattr(update, "user_id") else client.get_entity(update.message.from_id)
    except ValueError:
        telegramUser = None
    toUser = client.get_me()
    if telegramUser is None or toUser is None:
        return None
    from_social = getUserFromTelegramUser(telegramUser)
    to_social = getUserFromTelegramUser(toUser)
    if from_social is None or to_social is None or from_social == to_social:
        return None
    message['fromUser'] = from_social.user
    message['toUser'] = to_social.user
    message['content'] = update.message.message
    if hasattr(update.message, "media") and update.message.media is not None and \
            (isinstance(update.message.media, MessageMediaPhoto) or
                 isinstance(update.message.media, MessageMediaDocument)):
        path = client.download_media(
            update.message,
            file=os.path.join(settings.BASE_DIR, "temp"),
            progress_callback=download_progress_callback)
        message['file'] = File(open(path, "rb"))
        message['file'].name = os.path.basename(path)
    return message