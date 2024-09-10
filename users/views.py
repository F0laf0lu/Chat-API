from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOrReadOnly
from .serializers import UserSerializer, RegisterSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
     

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action == 'delete':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]