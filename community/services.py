from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from translator.models import InteractionLog, Preference, HasSocialNetwork


def getSocialPreferences(sender, receiver):
    socials = []

    logs = InteractionLog.objects.filter(fromUser=receiver, toUser=sender,
                                         timestamp__gte=timezone.now() - timedelta(hours=settings.PREFERENCES_HOURS))
    if len(logs) != 0:
        log = logs.latest("timestamp")
        socials.append(log.through)
    for preference in Preference.objects.filter(sender=sender, receiver=receiver).order_by('priority'):
        if preference.through not in socials:
            socials.append(preference.through)
    for hsn in HasSocialNetwork.objects.filter(user = sender):
        if hsn.social not in socials:
            socials.append(hsn.social)
    return socials