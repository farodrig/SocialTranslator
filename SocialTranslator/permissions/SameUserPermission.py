from rest_framework import permissions


class SameUserPermission(permissions.BasePermission):

    keys = ["user", "username", "fromUser"]
    message = "The consumer user should coincide with the username in one of these fields " + str(keys) + ". You can't impersonate someone."

    def has_permission(self, request, view):
        if (request.user.username == ""):
            return True
        for key in self.keys:
            if key in request.data:
                return request.user.username == request.data[key]
        return False