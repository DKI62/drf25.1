from rest_framework.permissions import BasePermission

from users.models import CustomUser


class IsOwner(BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта (CustomUser).
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, CustomUser):
            return obj.id == request.user.id
        return getattr(obj, 'owner', None) == request.user


class IsModerator(BasePermission):
    """
    Проверяет, состоит ли пользователь в группе "Модераторы".
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.groups.filter(name='Модераторы').exists()
