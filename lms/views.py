from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .models import Lesson, Course
from .serializers import LessonSerializer, CourseSerializer


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        """
        Показывать только уроки, принадлежащие авторизованному пользователю.
        Модераторы видят все уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            # Проверяем, что пользователь НЕ модератор
            if self.request.user.groups.filter(name='Модераторы').exists():
                self.permission_denied(
                    self.request,
                    message="Moderators are not allowed to create lessons."
                )
        return [IsAuthenticated()]


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT']:
            # Проверяем на владельца или модератора
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            # Удалять может только владелец
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Для всех остальных методов
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        # Проверка: запрещаем модераторам создание курсов
        if request.user.groups.filter(name='Модераторы').exists():
            raise PermissionDenied("Модераторам запрещено создавать курсы.")
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_moderator:  # Используем свойство `is_moderator`
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            if self.request.user.is_moderator:  # Модераторам запрещено создавать
                return [IsAuthenticated()]
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsOwnerOrModerator()]  # Только владелец или модератор
        elif self.action == 'destroy':
            return [IsOwner()]  # Только владелец
        return [IsAuthenticated()]
