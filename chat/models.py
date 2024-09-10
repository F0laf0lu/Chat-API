import uuid
from django.db import models
from django.contrib.auth import get_user_model

class ChatRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(get_user_model(), related_name='rooms', on_delete=models.CASCADE)
    members = models.ManyToManyField(get_user_model(), related_name='chatrooms')
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.room_name

class Message(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField()
    sender = models.ForeignKey(get_user_model(), related_name='messages', on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    date_sent = models.DateTimeField(auto_now_add=True)