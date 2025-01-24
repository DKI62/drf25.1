from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsModerator, IsOwner
from .models import Lesson, Course, Subscription, Payment
from .paginators import LessonPagination, CoursePagination
from .serializers import LessonSerializer, CourseSerializer, SubscriptionSerializer
from .services import create_stripe_product, create_stripe_price, create_stripe_session


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPagination

    @swagger_auto_schema(
        operation_description="Получить список уроков или создать новый урок.",
        responses={200: LessonSerializer(many=True)},
        request_body=LessonSerializer
    )
    def get_queryset(self):
        """
        Показывать только уроки, принадлежащие авторизованному пользователю.
        Модераторы видят все уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    @swagger_auto_schema(
        operation_description="Создать новый урок.",
        responses={201: LessonSerializer},
        request_body=LessonSerializer
    )
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

    @swagger_auto_schema(
        operation_description="Получить данные урока, обновить или удалить.",
        responses={200: LessonSerializer},
    )
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT']:
            # Разрешаем редактирование владельцам и модераторам
            self.permission_classes = [IsOwner | IsModerator]
        elif self.request.method == 'DELETE':
            # Удаление разрешено только владельцам
            self.permission_classes = [IsOwner]
        return [permission() for permission in self.permission_classes]

    @swagger_auto_schema(
        operation_description="Обновить или удалить урок.",
        responses={200: LessonSerializer},
        request_body=LessonSerializer
    )
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    @swagger_auto_schema(
        operation_description="Получить список курсов или создать новый курс.",
        responses={200: CourseSerializer(many=True)},
        request_body=CourseSerializer
    )
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Создать новый курс.",
        responses={201: CourseSerializer},
        request_body=CourseSerializer
    )
    def create(self, request, *args, **kwargs):
        # Проверка: запрещаем модераторам создание курсов
        if request.user.groups.filter(name='Модераторы').exists():
            raise PermissionDenied("Модераторам запрещено создавать курсы.")
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получить курсы авторизованного пользователя или все курсы для модераторов.",
        responses={200: CourseSerializer(many=True)}
    )
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

    @swagger_auto_schema(
        operation_description="Подписка или отписка от курса.",
        responses={200: "Subscription added.", 400: 'Bad Request', 404: 'Course not found'},
        request_body=SubscriptionSerializer
    )
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

    def delete(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        subscription = Subscription.objects.filter(user=request.user, course_id=course_id).first()
        if subscription:
            subscription.delete()
            return Response({"message": "Subscription removed."}, status=204)
        return Response({"error": "Subscription not found."}, status=404)


class PaymentCreateView(APIView):
    def post(self, request):
        product_name = request.data.get("product_name")
        product_price = request.data.get("product_price")

        if not product_name or not product_price:
            return Response({"error": "Product name and price are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем продукт и цену в Stripe
        try:
            stripe_product_id = create_stripe_product(product_name)
            stripe_price_id = create_stripe_price(stripe_product_id, int(product_price) * 100)
            stripe_session_url = create_stripe_session(stripe_price_id)

            # Сохраняем данные в БД
            payment = Payment.objects.create(
                product_name=product_name,
                product_price=int(product_price) * 100,
                stripe_product_id=stripe_product_id,
                stripe_price_id=stripe_price_id,
                stripe_session_url=stripe_session_url,
            )

            return Response({"payment_url": stripe_session_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Представление для успешной оплаты


def success_view(request):
    return HttpResponse("Оплата успешно завершена!")

    # Представление для отмененной оплаты


def cancel_view(request):
    return HttpResponse("Оплата отменена.")
