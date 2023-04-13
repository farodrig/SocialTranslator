import copy
import coreapi
import coreschema

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, schema, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.schemas import AutoSchema

from SocialTranslator.permissions.SameUserPermission import SameUserPermission
from translator.translators.Translator import Translator
from translator.models import HasSocialNetwork, SocialNetwork
from translator.services import sendMessage as send, configure as conf

@api_view(['POST'])
@parser_classes((MultiPartParser, JSONParser))
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "through",
            required=True,
            location='form',
            description="The social network through which the message will be sent",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "fromUser",
            required=True,
            location='form',
            description="Indicates the user that will send the message. The username or alias of the specified social network must be used",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "toUser",
            required=True,
            location='form',
            description="Indicates the user that will receive the message. The username or alias of the specified social network must be used",
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
    if 'fromUser' not in request.data or 'toUser' not in request.data or 'through' not in request.data:
        return Response({'detail': "fromUser, toUser and through are required parameters"},
                        status=status.HTTP_400_BAD_REQUEST)
    data = copy.copy(request.data)
    has_social = HasSocialNetwork.objects.filter(alias=data['fromUser'], social=data['through'])
    if len(has_social) != 1:
        has_social = HasSocialNetwork.objects.filter(username=data['fromUser'], social=data['through'])
        if len(has_social) != 1:
            message = "fromUser not founded for pair: {} - {}".format(data['fromUser'], data['through'])
            return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)
    has_social = has_social[0]
    data['fromUser'] = has_social.user.pk

    toUser = HasSocialNetwork.objects.filter(alias=data['toUser'], social=data['through'])
    if len(toUser) != 1:
        toUser = HasSocialNetwork.objects.filter(username=data['toUser'], social=data['through'])
        if len(toUser) != 1:
            message = "toUser not founded for pair: {} - {}".format(data['toUser'], data['through'])
            return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)
    data['toUser'] = toUser[0].user.pk
    data['kind'] = "output"

    response = send(data, has_social)
    sts = status.HTTP_404_NOT_FOUND if response.get('code') == Translator.ERROR_CODE else status.HTTP_200_OK
    return Response({'detail': response.get('detail')}, status=sts)


@api_view(['POST'])
@permission_classes((SameUserPermission, ))
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "username",
            required=True,
            location='form',
            description="Username or alias to configure access to social network",
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
    if "username" not in request.data or "social" not in request.data:
        return Response({'detail': "username and social are required parameters"}, status=status.HTTP_400_BAD_REQUEST)
    has_social = HasSocialNetwork.objects.filter(alias=request.data['username'], social=request.data['social'])
    if len(has_social) != 1:
        has_social = HasSocialNetwork.objects.filter(username=request.data['username'], social=request.data['social'])
        if len(has_social) != 1:
            message = "The username {} not related with social network {}".format(request.data['username'],
                                                                                  request.data['social'])
            return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)

    has_social = has_social[0]
    return conf(has_social, request.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
@schema(AutoSchema(
    manual_fields=[
        coreapi.Field(
            "state",
            required=True,
            location='query',
            description="Contains the user's identificator that was authenticated in the external system",
            schema=coreschema.String()
        ),
        coreapi.Field(
            "code",
            required=True,
            location='query',
            description="Contains the user's authentication code or token to use",
            schema=coreschema.String()
        ),
    ]
))
def authCallback(request, social):
    """
    Receive authentication callback from oauth2 authentication systems. For example, Gmail.
    """
    if not 'state' in request.query_params:
        return Response({'detail': "state with user must come on the query params"}, status=status.HTTP_400_BAD_REQUEST)
    user = request.query_params['state']

    if not 'code' in request.query_params:
        return Response({'detail': "code must come on the query params"}, status=status.HTTP_400_BAD_REQUEST)
    
    net = SocialNetwork.objects.filter(shortName=social)
    if len(net) != 1:
        return Response({'detail': "Social Network not supported"}, status=status.HTTP_400_BAD_REQUEST)
    net = net[0]

    has_social = HasSocialNetwork.objects.filter(alias=user, social=net)
    if len(has_social) != 1:
        has_social = HasSocialNetwork.objects.filter(username=user, social=net)
        if len(has_social) != 1:
            return Response({'detail': "User not founded"}, status=status.HTTP_404_NOT_FOUND)
    has_social = has_social[0]

    from translator.translators.TranslatorFactory import TranslatorFactory
    translator = TranslatorFactory.build(has_social)
    response = translator.configure({"username": has_social.username, "auth_code" : request.query_params['code']})

    sts = status.HTTP_404_NOT_FOUND if response.get('code') == Translator.ERROR_CODE else status.HTTP_200_OK
    return Response({'detail': response.get('detail')}, status=sts)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def pushNotification(request, social):
    """
    Receive push notifications from different social networks
    """
    net = SocialNetwork.objects.filter(shortName=social)
    if len(net) != 1:
        return Response({'detail': "Social Network not supported"}, status=status.HTTP_400_BAD_REQUEST)
    net = net[0]

    from translator.translators.TranslatorFactory import TranslatorFactory
    push_handler = TranslatorFactory.getPushHandler(net)
    response = push_handler(request.data)

    sts = status.HTTP_404_NOT_FOUND if response.get('code') == Translator.ERROR_CODE else status.HTTP_200_OK
    return Response({'detail': response.get('detail')}, status=sts)
