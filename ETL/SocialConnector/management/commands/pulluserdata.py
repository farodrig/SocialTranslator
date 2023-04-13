from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings

from ETL.SocialConnector.API import API
from community.utils import createUser, createProfile, createNewUser, createCommunity


class Command(BaseCommand):
    help = "Update users' data in app"

    def handle(self, *args, **options):
        addCommunities()


def addCommunities():
    communities = API.getAll()
    for community in communities:
        members = []
        assisted = User.objects.filter(username=community['grandpa']['user']).first()
        if assisted is None:
            community['grandpa']['pass'] = settings.SOCIALCONNECTOR_PASSWORD
            assisted = createUser(community['grandpa'])
            createProfile(assisted, community['grandpa'])

        for member in community['members']:
            member['pass'] = settings.SOCIALCONNECTOR_PASSWORD
            member['requires_assistant'] = member['is_grandpa']
            user = createNewUser(member, assisted)
            members.append(user)

        createCommunity(members, "Comunidad de " + assisted.get_full_name())
