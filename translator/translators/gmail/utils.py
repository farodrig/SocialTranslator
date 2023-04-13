import mimetypes
import os
import email
import base64
import quopri
import logging

from io import BytesIO

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.core.files import File

from email_reply_parser import EmailReplyParser

from apiclient import errors
from googleapiclient.http import MediaIoBaseUpload

from translator.translators.utils import getUsernameFromMessage

subject = "Mensaje de Abuelo {}"
logger = logging.getLogger(__name__)

def getListHistory(service, user_id, start_history_id='1'):
    """List History of all changes to the user's mailbox.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    start_history_id: Only return Histories at or after start_history_id.

    Returns:
    A list of mailbox changes that occurred after the start_history_id.
    """
    try:
        history = (service.users().history().list(userId=user_id, startHistoryId=start_history_id).execute())
        changes = history['history'] if 'history' in history else []
        while 'nextPageToken' in history:
            page_token = history['nextPageToken']
            history = (service.users().history().list(userId=user_id,
                                            startHistoryId=start_history_id,
                                            pageToken=page_token).execute())
            changes.extend(history['history'])
        return changes
    except errors.HttpError as error:
        logger.error('An error occurred: %s' % error)
    return []

def getLastHistoryId(service, user):
    try:
        response = service.users().messages().list(userId=user, maxResults=1,
                                                   labelIds=['CATEGORY_PERSONAL', 'UNREAD', 'INBOX']).execute()
        if 'messages' in response:
            message = service.users().messages().get(userId=user, id=response['messages'][0]['id']).execute()
            return str(message['historyId'])

    except errors.HttpError as error:
        logger.error('An error occurred: %s' % error)
    return '0'

def getMessagesFromHistories(service, user, histories, labelIds=[], messages_ids =[]):
    messages = []
    fields = ["messagesAdded"]
    for history in histories:
        for field in fields:
            if field not in history:
                continue
            for message in history[field]:
                message = message['message']
                if message['id'] not in messages_ids and set(labelIds).issubset(set(message['labelIds'])):
                    messages.append(getMimeMessage(service, user, message['id']))
                    messages_ids.append(message['id'])

        if "messages" not in history:
            continue
        for message in history['messages']:
            if message['id'] not in messages_ids:
                m = getMessage(service, user, message['id'])
                if set(labelIds).issubset(set(m['labelIds'])):
                    messages.append(getMimeMessage(service, user, m['id']))
                    messages_ids.append(m['id'])

    return messages

def getMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message
    except errors.HttpError as error:
        logger.error('An error occurred: %s' % error)
        return None


def getMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Returns:
    A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')

        mime_msg = email.message_from_string(msg_str)
        mime_msg['id'] = msg_id
        return mime_msg
    except errors.HttpError as error:
        logger.error('An error occurred: %s' % error)
        return None


def create_message(msg):
    """Create a message for an email.

    Returns:
    An object containing a base64url encoded email object.
    """
    bytes_message = BytesIO()

    fromUser, toUser = getUsernameFromMessage(msg)

    message = MIMEMultipart() if msg.file.name is not None else MIMEText(msg.content)
    message['to'] = toUser
    message['from'] = fromUser
    message['subject'] = subject.format(msg.fromUser.first_name)


    if msg.file.name is None:
        bytes_message.write(base64.urlsafe_b64decode(base64.urlsafe_b64encode(message.as_string().encode())))
        return MediaIoBaseUpload(bytes_message, mimetype='message/rfc822')

    path = msg.file.path
    if (msg.content is not None):
        att = MIMEText(msg.content)
        message.attach(att)

    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(path, 'rb')
        att = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        att = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        att = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(path, 'rb')
        att = MIMEBase(main_type, sub_type)
        att.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(path)
    att.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(att)

    bytes_message.write(base64.urlsafe_b64decode(base64.urlsafe_b64encode(message.as_string().encode())))
    return MediaIoBaseUpload(bytes_message, mimetype='message/rfc822')


def getBodyFromMessage(msg):
    text = ""
    if isinstance(msg,dict) and "content" in msg:
        return msg["content"]
    if msg.is_multipart():
        for payload in msg.get_payload():
            if payload.get_content_type() == "text/plain":
                text += quopri.decodestring(payload.get_payload()).decode(payload.get_content_charset())
            elif payload.get_content_type() == "multipart/alternative":
                text += getBodyFromMessage(payload)
    else:
        text = msg.get_payload()
    return EmailReplyParser.parse_reply(text)


def getAttachments(service, user_id, msg_id, store_dir=""):
  files = []
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
  except errors.HttpError as error:
    logger.error('An error occurred: %s' % error)
  else:
      for part in message['payload']['parts']:
          if part['filename']:
              if 'data' in part['body']:
                  data = part['body']['data']
              else:
                  att_id = part['body']['attachmentId']
                  att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,
                                                                     id=att_id).execute()
                  data = att['data']
              file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
              path = os.path.join(store_dir, part['filename'])

              with open(path, 'wb') as f:
                  f.write(file_data)
              f = File(open(path, "rb"))
              f.name = os.path.basename(path)
              files.append(f)
  return files