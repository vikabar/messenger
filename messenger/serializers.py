from rest_framework import serializers
from django.contrib.auth.models import User
from messenger.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    receiver = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = Message
        fields = ['id', 'message_body', 'message_subject', 'sender', 'receiver', 'creation_date']

