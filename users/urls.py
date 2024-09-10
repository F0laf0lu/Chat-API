from django.urls import path
from .views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls

urlpatterns += [
    path('auth/login', TokenObtainPairView.as_view(), name='user-login'),
    path('auth/login/refresh', TokenRefreshView.as_view(), name='token-refresh')
]