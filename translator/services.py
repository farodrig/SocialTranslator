from rest_framework import status
from rest_framework.response import Response

from translator.models import Message, HasSocialNetwork
from translator.serializers import MessageSerializer
from translator.translators.Translator import Translator
from translator.translators.TranslatorFactory import TranslatorFactory


def sendMessage(data, sender):
    from translator.utils import saveInteractionLog

    serializer = MessageSerializer(data=data)
    if not serializer.is_valid():
        message = "serializer failed with errors: " + str(serializer.errors)
        return {'detail': message, 'code': Translator.ERROR_CODE}
    message = Message(**serializer.validated_data)

    if message.content is None and message.file is None:
        return {'detail': "At least one of fields 'content' or 'file' mustn't be empty", 'code': Translator.ERROR_CODE }

    translator = TranslatorFactory.build(sender)
    if translator is None:
        return {'detail': "{} is not currently supported for sending messages".format(message.through),
                'code': Translator.ERROR_CODE }
    send = translator.getSendFunction(message)
    message.save()

    response = send(message)

    message.ack = response.get('code') == Translator.SUCCESS_CODE
    message.save()
    if message.ack:
        saveInteractionLog(message)
    return response


def configure(has_social, data):
    data['username'] = has_social.username

    translator = TranslatorFactory.build(has_social)
    answer = translator.configure(data)

    sts = status.HTTP_404_NOT_FOUND if answer.get('code') == Translator.ERROR_CODE else status.HTTP_200_OK
    result = {'detail': answer.get('detail')}
    if "redirectURL" in answer:
        result['redirectURL'] = answer.get('redirectURL')
    return Response(result, status=sts)

def connect(has_social: HasSocialNetwork):
    translator = TranslatorFactory.build(has_social)
    answer = translator.isConnected()

    sts = status.HTTP_200_OK if answer else status.HTTP_404_NOT_FOUND
    return Response(status=sts)


def checkNetworkStatus(user, social):
    has_social = HasSocialNetwork.objects.filter(user=user, social=social)
    if len(has_social) != 1:
        if len(has_social) == 0:
            return {'detail': "User don't have an account in Social Network", 'code': status.HTTP_400_BAD_REQUEST}
        return {'detail': "User have more than one account in Social Network. It's not permitted", 'code': status.HTTP_403_FORBIDDEN}
    has_social = has_social[0]
    translator = TranslatorFactory.getTranslator(has_social.pk)
    if translator is None or not translator.isConnected():
        return {'detail': "User should configure that Social Network to use it", 'code': status.HTTP_404_NOT_FOUND}
    return {'detail': "User is currently logged in Social Network", 'code': status.HTTP_200_OK}