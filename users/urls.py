from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, PaymentListView

router = DefaultRouter()
router.register('', CustomUserViewSet, basename='user')

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),  # Сначала маршрут для платежей
    path('', include(router.urls)),  # Затем маршруты роутера
]