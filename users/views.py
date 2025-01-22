from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import CustomUser, Payment
from .permissions import IsOwner
from .serializers import CustomUserSerializer, PaymentSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        elif self.action == 'list':
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Модераторы').exists():
            return CustomUser.objects.all()
        # Если пользователь пытается получить доступ к чужому профилю
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            if not CustomUser.objects.filter(id=user.id).exists():
                raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(id=user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Проверка: пользователь может удалить только свой профиль
        if instance != request.user:
            raise PermissionDenied("You do not have permission to delete this profile.")
        return super().destroy(request, *args, **kwargs)


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['date']
