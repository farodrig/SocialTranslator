from django.contrib import admin
from .models import Message, SocialNetwork, HasSocialNetwork, InteractionLog, Preference
from itertools import chain
# Register your models here.

def getAllFields(MyModel):
    result = []
    for field in MyModel._meta.get_fields():
        if field.many_to_one is False:
            continue
        result.append(field.name)
    return result

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = getAllFields(Message)
    pass

@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = getAllFields(SocialNetwork)

@admin.register(HasSocialNetwork)
class HasSocialNetworkAdmin(admin.ModelAdmin):
    list_display = getAllFields(HasSocialNetwork)

@admin.register(InteractionLog)
class InteractionLogAdmin(admin.ModelAdmin):
    list_display = getAllFields(InteractionLog)

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = getAllFields(Preference)
