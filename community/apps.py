from django.apps import AppConfig

class CommunityConfig(AppConfig):
    name = 'community'

    def ready(self):
        initialPullExternalUsersData()


def initialPullExternalUsersData():
    from ETL.SocialConnector.management.commands.pulluserdata import addCommunities
    addCommunities()
