from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command

from preferences.UserPreferences import UserPreferences
from translator.models import HasSocialNetwork, Preference


class Command(BaseCommand):
    help = "Update users' preferences2 in external app"

    def handle(self, *args, **options):
        updatePreferences()

def updatePreferences():
    assistedUsers = User.objects.filter(profile__requires_assistant=True)
    for assisted in assistedUsers:
        families = assisted.family_set.all()
        for family in families:
            for member in family.members.all():
                if member == assisted:
                    continue
                has_socials = HasSocialNetwork.objects.filter(user=member)
                preferences = []
                for has_social in has_socials:
                    preference = UserPreferences(member, has_social.social, assisted)
                    preferences.append((sum(preference.forecast), has_social.social))
                preferences.sort(key=lambda x: x[0], reverse=True)
                for index, preference in enumerate(preferences):
                    social = preference[1]
                    pref, created = Preference.objects.get_or_create(sender=assisted, receiver=member, through=social)
                    pref.priority = index + 1
                    pref.save()
    call_command('pushpreferences')