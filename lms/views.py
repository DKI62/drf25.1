from rest_framework import generics, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsModerator, IsOwner
from .models import Lesson, Course, Subscription
from .paginators import LessonPagination, CoursePagination
from .serializers import LessonSerializer, CourseSerializer


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPagination

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
        if self.request.method == 'POST' and self.request.user.is_moderator:
            raise PermissionDenied("Модераторам запрещено создавать уроки.")
        return super().get_permissions()


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT']:
            # Разрешаем редактирование владельцам и модераторам
            self.permission_classes = [IsOwner | IsModerator]
        elif self.request.method == 'DELETE':
            # Удаление разрешено только владельцам
            self.permission_classes = [IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        # Проверка: запрещаем модераторам создание курсов
        if request.user.groups.filter(name='Модераторы').exists():
            raise PermissionDenied("Модераторам запрещено создавать курсы.")
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_moderator:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            # Модераторам запрещено создавать
            if self.request.user.is_moderator:
                raise PermissionDenied("Модераторам запрещено создавать курсы.")
        elif self.action in ['update', 'partial_update']:
            # Только владелец или модератор
            self.permission_classes = [IsOwner | IsModerator]
        elif self.action == 'destroy':
            # Удаление разрешено только владельцам
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')  # Получаем ID курса
        if not course_id:
            return Response({"message": "Course ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response({"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        # Проверка, есть ли уже подписка
        subscription, created = Subscription.objects.get_or_create(user=user, course=course)
        if created:
            message = 'Subscription added.'
        else:
            # Если подписка существует, удаляем ее
            subscription.delete()
            message = 'Subscription removed.'

        return Response({"message": message}, status=status.HTTP_200_OK)
