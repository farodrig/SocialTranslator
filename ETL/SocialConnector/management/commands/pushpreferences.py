from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from ETL.SocialConnector.API import API
from translator.models import Preference


class Command(BaseCommand):
    help = "Update users' preferences in external app"

    def handle(self, *args, **options):
        def getPreferences(sender, receiver):
            prefs = []
            data = {
                'user': sender.username,
                'preferences': prefs
            }
            preferences = Preference.objects.filter(sender=sender, receiver=receiver)
            for preference in preferences:
                prefs.append({
                    'network': preference.through.shortName,
                    'order': preference.priority
                })
            return data

        receivers = User.objects.filter(profile__requires_assistance=True)

        for receiver in receivers:
            senders = Preference.objects.filter(receiver=receiver).values_list('sender', flat=True)\
                .order_by('sender').distinct()
            for sender in senders:
                sender = User.objects.get(pk=sender)
                data = getPreferences(sender, receiver)

                result = API.postPreferences(receiver.username, [data])

                message = "preferences between {} and {} in external system".format(str(receiver), str(sender))
                message = self.style.SUCCESS("Updated " + message) if result else self.style.ERROR("Error updating " + message)
                self.stdout.write(message)
