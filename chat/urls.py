from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet


router = DefaultRouter()
router.register('', ChatRoomViewSet, basename='chatroom')

urlpatterns = router.urls
