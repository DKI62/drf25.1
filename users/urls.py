from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CustomUserViewSet, PaymentListView

router = DefaultRouter()
router.register('', CustomUserViewSet, basename='user')

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),  # Сначала маршрут для платежей
    path('', include(router.urls)),  # Затем маршруты роутера
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]