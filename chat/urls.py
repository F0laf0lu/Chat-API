from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet


router = DefaultRouter()
router.register('chatroom', ChatRoomViewSet, basename='chatroom')

urlpatterns = router.urls
