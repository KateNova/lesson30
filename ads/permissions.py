from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

from user.models import User


class AdUpdateDeletePermission(permissions.IsAuthenticated):
    message = 'Update and Delete ads only for authors, moderators and admins.'

    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False
        if request.user.role in [User.MODERATOR, User.ADMIN]:
            return True
        if request.user == obj.author:
            return True
        return False


class SelectionPermission(permissions.IsAuthenticated):
    message = 'Create for auth users; Update and Delete only for owners'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return obj.owner == request.user
