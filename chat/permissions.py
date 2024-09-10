from rest_framework.permissions import BasePermission, SAFE_METHODS
from chat.models import ChatRoom

class IsChatRoomCreator(BasePermission):

    def  has_object_permission(self, request, view, chatroom):
        if request.method in SAFE_METHODS:
            return True
        
        return request.user == chatroom.creator
    
class CanAdduser(BasePermission):
    def has_permission(self, request, view):
        chatroom = ChatRoom.objects.get(room_id=view.kwargs['room_id'])
        return chatroom.creator == request.user

class GetMember(BasePermission):
    def has_permission(self, request, view):
        chatroom = ChatRoom.objects.get(room_id=view.kwargs['room_id'])
        if chatroom.creator == request.user or request.user.is_admin:
            return True 

    def  has_object_permission(self, request, view, chatroom):
        if request.method in SAFE_METHODS:
            return True
        
        return request.user == chatroom.creator
    
class ChatRoomMember(BasePermission):
    def has_permission(self, request, view):
        chatroom_members = ChatRoom.objects.get(room_id=view.kwargs['room_id']).members.all()
        if request.user in chatroom_members:
            return True