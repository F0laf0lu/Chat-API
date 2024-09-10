from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import ChatRoom
from .serializers import ChatRoomSerializer, CreateChatRoomSerializer,  AddUserToRoomSerializer, MemberSerializer, ChatRoomMemberSerializer, SendChatSerializer
from .permissions import IsChatRoomCreator, CanAdduser, GetMember, ChatRoomMember


class ChatRoomViewSet(ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    lookup_field = 'room_id'
    permission_classes  = [IsAuthenticated]

    def get_serializer_context(self):
        return super().get_serializer_context()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChatRoomSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action in ['partial_update', 'update', 'delete']:
            permission_classes = [IsChatRoomCreator]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[CanAdduser], serializer_class=AddUserToRoomSerializer)
    def add_member(self, request, **kwargs):
        serializer = AddUserToRoomSerializer(data=request.data, context={'room_id':self.kwargs['room_id']})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, permission_classes=[IsAdminUser, IsChatRoomCreator])
    def get_members(self, request, **kwargs):
        room_id = self.kwargs['room_id']
        members = ChatRoom.objects.get(room_id=room_id)
        serializer = MemberSerializer(members)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'delete'], url_path='member/(?P<user_id>[^/.]+)')
    def member(self, request, **kwargs):
        chat_room = self.get_object()
        user_id = kwargs['user_id']
        user = get_object_or_404(chat_room.members, id=user_id)

        if request.method == 'GET':
            serializer = ChatRoomMemberSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if user == chat_room.creator:
                return Response({'detail': 'Chat room creator cannot be removed'}, status=status.HTTP_400_BAD_REQUEST)
            chat_room.members.remove(user)
            return Response({'detail': 'User removed successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], permission_classes=[ChatRoomMember], serializer_class=SendChatSerializer)
    def chat(self, request, **kwargs):
        room = get_object_or_404(ChatRoom, room_id=self.kwargs['room_id'])

        channel_room_name = room.room_name.replace(' ', '-').lower()[:99]
        if request.method ==  'GET':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                        f'chat_{channel_room_name}', 
                        {"type": "send_info_to_user_group",
                        "text": {"message": f"{request.user.username} joined chat"}})
            return Response({'success': 'User joined chat'}, status=status.HTTP_200_OK)

        if request.method == 'POST':
            serializer = SendChatSerializer(data=request.data, context={'room_id':self.kwargs['room_id'], 'user':request.user})
            serializer.is_valid(raise_exception=True)
            message = serializer.save()
            socket_message = f"Message with id {message.id} was created!"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{channel_room_name}', 
                {
                    'type': 'chat_message', 
                    'message': socket_message,
                    'message_id': message.message_id,
                    'user': request.user.username,
                    'room_name': room.room_name
                }
            )
            return Response({"status": True}, status=status.HTTP_201_CREATED)