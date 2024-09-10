from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateField(read_only = True)
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(field, value):
        if value is None:
            raise serializers.ValidationError('Username is required')
        return value
    
    def validate(self, attrs):
        if len(attrs['password']) < 8:
            raise serializers.ValidationError('Password should be at least 8 characters')
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'])
        
        return user