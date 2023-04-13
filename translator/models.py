from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver

# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    return 'user_{0}/{1}'.format(instance.fromUser.username, filename)


class SocialNetwork(models.Model):
    shortName = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=300)
    users = models.ManyToManyField(User, through='HasSocialNetwork')
    pushNotification = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class HasSocialNetwork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social = models.ForeignKey(SocialNetwork, on_delete=models.CASCADE)
    username = models.CharField(max_length=300)
    alias = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        unique_together = (("user", "social"),
                           ("social", "username"))

    def __str__(self):
        return self.user.get_full_name() + " - " + str(self.social)


class Preference(models.Model):
    sender = models.ForeignKey(User, related_name="sender_priorities")
    receiver = models.ForeignKey(User, related_name="receiver_priorities")
    through = models.ForeignKey(SocialNetwork)
    priority = models.IntegerField(default=1)

    class Meta:
        unique_together = (("sender", "receiver", "through"),)

    def __str__(self):
        return self.sender.get_full_name() + " - " + \
               self.receiver.get_full_name() + " - " + \
               str(self.through) + " - " + str(self.priority)


class Message(models.Model):
    KIND_CHOICES = (
        ('input', 'Recibido'),
        ('output', 'Enviado')
    )
    fromUser = models.ForeignKey(User, related_name="sent_messages")
    toUser = models.ForeignKey(User, related_name="received_messages")
    through = models.ForeignKey(SocialNetwork)
    kind = models.CharField(max_length=6, choices=KIND_CHOICES)
    ack = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=user_directory_path, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sourceID = models.CharField(max_length=512, blank=True, null=True)


@receiver(pre_delete, sender=Message)
def message_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


class InteractionLog(models.Model):
    MEDIA_TYPE = (
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('image', 'Imagen'),
        ('text', 'Texto'),
        ('videocall', 'Videollamada')
    )
    fromUser = models.ForeignKey(User, related_name="sent_logs")
    toUser = models.ForeignKey(User, related_name="received_logs")
    through = models.ForeignKey(SocialNetwork)
    media = models.CharField(max_length=10, choices=MEDIA_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)
    final_timestamp = models.DateTimeField(null=True, blank=True)