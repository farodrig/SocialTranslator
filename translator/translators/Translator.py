import mimetypes
from abc import ABC, abstractmethod


class Translator(ABC):

    MORE_INFO_CODE = 1 # Indicate that the method need more info or optional parameters
    SUCCESS_CODE = 2 # Indicate that the method finished correctly
    ERROR_CODE = 4 # Indicate that the method fail in the task

    @abstractmethod
    def __init__(self, user, listen = False):
        pass

    @abstractmethod
    def isConnected(self):
        pass

    @abstractmethod
    def configure(self, data):
        pass

    @abstractmethod
    def sendText(self, message):
        pass

    @abstractmethod
    def sendImage(self, message):
        pass

    @abstractmethod
    def sendVideo(self, message):
        pass

    @abstractmethod
    def sendAudio(self, message):
        pass

    def getSendFunction(self, message):
        if message.content is not None and message.file.name is None:
            return self.sendText
        if message.file.name is not None:
            if hasattr(message.file.file, "content_type"):
                kind = message.file.file.content_type
            else:
                kind = mimetypes.guess_type(message.file.url)[0]

            if "image" in kind:
                return self.sendImage
            elif "audio" in kind:
                return self.sendAudio
            elif "video" in kind:
                return self.sendVideo
        raise ValueError("Not supported operation for this kind of message")
