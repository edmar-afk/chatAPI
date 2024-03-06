from .models import User, Message
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, generics
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Include 'date_joined' field

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.first_name
        # ...

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('first_name', 'username', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message', 'sender', 'receiver', 'sent_time']


class DisplayMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'message', 'sender', 'receiver', 'sent_time']
        
class DisplaySenderSerializer(serializers.ModelSerializer):
    model = Message
    
    

# class MessageReadStatusSerializer(serializers.ModelSerializer):
#     sender_unread_count = serializers.SerializerMethodField()
#     receiver_unread_count = serializers.SerializerMethodField()

#     class Meta:
#         model = MessageReadStatus
#         fields = ['message', 'user', 'is_read', 'sender_unread_count', 'receiver_unread_count']

#     def get_sender_unread_count(self, obj):
#         # Get the count of unread messages for the sender
#         return MessageReadStatus.objects.filter(message__sender=obj.message.sender, is_read=False).count()

#     def get_receiver_unread_count(self, obj):
#         # Get the count of unread messages for the receiver
#         return MessageReadStatus.objects.filter(message__receiver=obj.message.receiver, is_read=False).count()