import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import  ChatRoom


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_name = ChatRoom.objects.get(room_id=self.room_id).room_name.replace(' ', '-').lower()[:99]
        self.room_group_name = f'chat_{self.room_name}'
        
        if self.scope['user'] is not AnonymousUser:
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive chats from room group
    def chat_message(self, event):
        message = event
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))

    # user acceses chat 
    def send_info_to_user_group(self, event):
        message = event["text"]
        self.send(text_data=json.dumps(message))