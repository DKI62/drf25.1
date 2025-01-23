from rest_framework.permissions import BasePermission

from users.models import CustomUser


class IsOwner(BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта (CustomUser или другого объекта с полем owner).
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, если объект — пользователь
        if isinstance(obj, CustomUser):
            return obj == request.user  # Сравнение объекта пользователя напрямую
        # Проверяем, есть ли у объекта атрибут owner и сравниваем с текущим пользователем
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsModerator(BasePermission):
    """
    Проверяет, состоит ли пользователь в группе "Модераторы".
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


