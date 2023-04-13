from django.contrib import admin

from community.models import Community, UserProfile


def getAllFields(MyModel):
    result = []
    for field in MyModel._meta.get_fields():
        if field.many_to_one is False:
            continue
        result.append(field.name)
    return result

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = getAllFields(Community)
    pass

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = getAllFields(UserProfile)
    pass
