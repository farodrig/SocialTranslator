import logging
import operator
from functools import reduce

from django.db.models import Q, Count
from django.contrib.auth.models import User

from community.models import Community, UserProfile
from translator.models import SocialNetwork, HasSocialNetwork, Preference

logger = logging.getLogger(__name__)

def shareCommunity(user, assisted):
    if not assisted.profile.requires_assistant:
        return False
    for community in assisted.community_set.all():
        if user in community.members.all():
            return True
    return False


def createCommunity(members, name=""):
    community = Community.objects.filter(name=name).first()
    if community is None:
        query = reduce(operator.and_, (Q(members__id=member.id) for member in members))
        community = Community.objects.annotate(num_members=Count('members'))\
            .filter(num_members=len(members))\
            .exclude(~query)\
            .first()
        if community is None:
            community = Community(name=name)
            community.save()

    community.name = name
    community.members = members
    community.save()


def createUser(data):
    user = User.objects.filter(username=data['user']).first()
    if user is not None:
        logger.info("user {} already exist".format(data['user']))
    else:
        user = User.objects.create_user(data['user'], password=data["pass"] if "pass" in data else "server123")
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.save()
    return user


def createProfile(user, data):
    profile = UserProfile.objects.filter(user=user).first()
    if profile is not None:
        logger.info("user profile from {} already exist".format(data['user']))
        profile.requires_assistant = data['requires_assistant']
    else:
        profile = UserProfile(user=user, requires_assistant=data['requires_assistant'])
    profile.save()


def createNewUser(member, receiver):
    from translator.utils import userChangePreference

    user = createUser(member)
    createProfile(user, member)
    for preference in member['preferences']:
        createHasSocial(preference, user)

        sn = SocialNetwork.objects.filter(name__icontains=preference['network']).first()
        if sn is None:
            logger.info("Not founded similar Social Network")
            continue

        pref = Preference.objects.filter(sender=user, receiver=receiver, through=sn).first()
        if pref is not None:
            continue

        try:
            userChangePreference(user, receiver, preference)
        except Exception as e:
            logger.error(e)
    return user

def createHasSocial(data, user):
    sn = SocialNetwork.objects.filter(name__icontains=data['network']).first()
    if sn is None:
        logger.info("Not founded similar Social Network")
        return
    isUsed = HasSocialNetwork.objects.filter(username=data['username'], social=sn).first()
    if isUsed is not None and isUsed.user != user:
        logger.info("username {} is already used for another user in social network {}".format(isUsed.username, sn.name))
        return
    has_sn = HasSocialNetwork.objects.filter(user=user, social=sn).first()
    if has_sn is None:
        has_sn = HasSocialNetwork(social=sn, user=user)
    has_sn.username = data['username']
    has_sn.save()
