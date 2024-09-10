from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    total_members = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = ['room_id', 'room_name', 'creator','total_members','date_created']

    def get_total_members(self, chatroom):
        total = chatroom.members.count()
        return total
    
class CreateChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['room_name', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        chatroom = ChatRoom.objects.create(
            room_name = validated_data['room_name'],
            description = validated_data['description'],
            creator = user
        )
        chatroom.members.add(user)

        return chatroom

class AddUserToRoomSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, username):
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('This user does not exist')
        return username

    def create(self, validated_data):
        room_id = self.context['room_id']
        chatroom = ChatRoom.objects.get(room_id=room_id)
        user = get_user_model().objects.get(username=validated_data['username'])
        chatroom.members.add(user)
        return user

class MemberSerializer(serializers.ModelSerializer):
    members = serializers.StringRelatedField(many=True)
    class Meta:
        model = ChatRoom
        fields = ['members']

class ChatRoomMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name']

class SendChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields  = ['content']

    def create(self, validated_data):
        user = self.context['user']
        room_id = self.context['room_id']
        chatroom = ChatRoom.objects.get(room_id=room_id)
        message  = Message.objects.create(
            content = validated_data['content'],
            sender = user,
            room = chatroom,
        )
        return message