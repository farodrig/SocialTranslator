import copy
import coreapi
import coreschema
import logging

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, schema, permission_classes
from rest_framework.schemas import AutoSchema

from SocialTranslator.permissions.SameUserPermission import SameUserPermission
from translator.models import HasSocialNetwork, Message, SocialNetwork
from translator.serializers import MessageSerializer
from translator.translators.Translator import Translator
from translator.services import sendMessage as send, configure as conf, checkNetworkStatus
from translator.utils import saveInteractionLog

from .services import getSocialPreferences
from community.utils import shareCommunity

logger = logging.getLogger(__name__)

@api_view(['POST'])
@parser_classes((MultiPartParser, JSONParser))
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "fromUser",
            required=True,
            location='form',
            description="The username of who will send the message",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "toUser",
            required=True,
            location='form',
            description="The username of who will receive the message",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "content",
            required=False,
            location='form',
            description="Text message that will be sent",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "file",
            required=False,
            location='form',
            description="File that will be sent",
            type="file"
        ),
    ]
))
def sendMessage(request):
    """
    Allows to send a message through a specific social network, from a specific user, to a specific user.
    """
    data = copy.copy(request.data)
    fromUser = User.objects.get(username = data['fromUser'])
    if fromUser is None:
        return Response({'detail': "not recognized username or id in 'fromUser' field"}, status=status.HTTP_404_NOT_FOUND)
    if not fromUser.profile.requires_assistant:
        return Response({'detail': "just users who indicates that requires assistant can send messages"}, status=status.HTTP_403_FORBIDDEN)

    toUser = User.objects.get(username = data['toUser'])
    if toUser is None:
        return Response({'detail': "not recognized username or id in 'toUser' field"}, status=status.HTTP_404_NOT_FOUND)

    if not shareCommunity(toUser, fromUser):
        return Response({'detail': "the users doesn't share the same community"}, status=status.HTTP_403_FORBIDDEN)

    data['fromUser'] = fromUser.pk
    data['toUser'] = toUser.pk
    data['kind'] = "output"

    socials = getSocialPreferences(fromUser, toUser)

    response = None
    for social in socials:

        data['through'] = social.pk

        has_social = HasSocialNetwork.objects.filter(user=fromUser, social=social)
        if len(has_social) < 1:
            message = "user {} don't have username for {}".format(data['fromUser'], data['through'])
            return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)
        has_social = has_social[0]

        response = send(data, has_social)
        if response.get('code') == Translator.SUCCESS_CODE:
            return Response({'detail': response.get('detail')}, status=status.HTTP_200_OK)
    return Response({'detail': response.get('detail')}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "user",
            required=True,
            location='form',
            description="The username of whom the access to the social network will be configured",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "social",
            required=True,
            location='form',
            description="Social network to configure access",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "auth_code",
            required=False,
            location='form',
            description="Contains the user's authentication code or token to use",
            schema=coreschema.String()
        ),
    ]
))
def configure(request):
    """
    Allow to configure a Social Network Translator for a specific user
    """
    has_social = HasSocialNetwork.objects.filter(user__username=request.data['user'], social=request.data['social'])
    if len(has_social) != 1:
        message = "The user {} not related with social network {}".format(request.data['user'], request.data['social'])
        return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)

    return conf(has_social[0], request.data)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "user",
            required=True,
            location='form',
            description="The username of who will be checked the new messages",
            schema=coreschema.String()
        ),
    ]
))
def checkMessages(request):
    """
    Allow to check for new messages to a specific user
    """
    user = User.objects.get(username=request.data['user'])
    if user is None:
        return Response({'detail': "not recognized user id in 'user' field"}, status=status.HTTP_404_NOT_FOUND)

    if not user.profile.requires_assistant:
        return Response({'detail': "user should require assistant"}, status=status.HTTP_403_FORBIDDEN)

    messages = Message.objects.filter(toUser=user, ack=False, kind="input")
    return Response({'news': len(messages) > 0, 'count': len(messages)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "user",
            required=True,
            location='form',
            description="The username of who will be checked the new messages",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "acks",
            required=False,
            location='form',
            description="The ids of the received messages",
            schema=coreschema.Array(items=coreschema.String())
        ),
    ]
))
def getMessages(request):
    """
    Allow to get new messages to a specific user
    """
    user = User.objects.get(username=request.data['user'])
    if user is None:
        return Response({'detail': "not recognized user id in 'user' field"}, status=status.HTTP_404_NOT_FOUND)

    if not user.profile.requires_assistant:
        return Response({'detail': "user should require assistant"}, status=status.HTTP_403_FORBIDDEN)

    if "acks" in request.data:
        deleted = []
        for id in request.data['acks']:
            try:
                m = Message.objects.get(pk=id)
                m.delete()
                deleted.append(id)
            except Exception as e:
                logger.error(e)
                
        return Response({'deleted': deleted, 'count':len(deleted)}, status=status.HTTP_200_OK)
    messages = Message.objects.filter(toUser=user, ack=False, kind="input")
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "user",
            required=True,
            location='form',
            description="The username of who will be checked the social networks status",
            schema=coreschema.String()
        ),
    ]
))
def checkNetworks(request):
    """
    Allow to check the social network status for a specific user
    """
    data = request.data
    user = User.objects.get(username = data['user'])
    if user is None:
        return Response({'detail': "not recognized username or id in 'user' field"}, status=status.HTTP_404_NOT_FOUND)
    if not user.profile.requires_assistant:
        return Response({'detail': "just users who requires assistant can check Social Network status"}, status=status.HTTP_403_FORBIDDEN)
    response = {}
    for sn in SocialNetwork.objects.all():
        response[sn.pk] = checkNetworkStatus(user, sn)
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "fromUser",
            required=True,
            location='form',
            description="The username of who sent the message",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "toUser",
            required=True,
            location='form',
            description="The username of who received the message",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "through",
            required=True,
            location='form',
            description="The social network through which the message was sent",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "media",
            required=True,
            location='form',
            description="The kind of interaction. Ex: Videocall",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "started",
            required=False,
            location='form',
            description="The datetime when interaction started",
            schema=coreschema.String(format="datetime-local") #datetime-local not working
        ),
        coreapi.Field(
            "ended",
            required=False,
            location='form',
            description="The datetime when interaction ended",
            schema=coreschema.String(format="datetime-local") #datetime-local not working
        ),
    ]
))
def register(request):
    """
    Allow to register an interaction between two users through a specific social network
    """
    data = request.data
    fromUser = User.objects.get(username = data['fromUser'])
    if fromUser is None:
        return Response({'detail': "not recognized username or id in 'fromUser' field"}, status=status.HTTP_404_NOT_FOUND)
    if not fromUser.profile.requires_assistant:
        return Response({'detail': "just users who requires assistant can register interaction"}, status=status.HTTP_403_FORBIDDEN)

    toUser = User.objects.get(username = data['toUser'])
    if toUser is None:
        return Response({'detail': "not recognized username or id in 'toUser' field"}, status=status.HTTP_404_NOT_FOUND)

    if not shareCommunity(toUser, fromUser):
        return Response({'detail': "the users doesn't share the same community"}, status=status.HTTP_403_FORBIDDEN)

    sn = SocialNetwork.objects.filter(name__icontains=data['through']).first()
    if sn is None:
        return Response({'detail': "social network {} not supported".format(data['through'])}, status=status.HTTP_403_FORBIDDEN)

    message = Message()
    message.fromUser = fromUser
    message.toUser = toUser
    message.through = sn
    saveInteractionLog(message, **data)

    return Response({'detail': "registered successfully"}, status=status.HTTP_200_OK)