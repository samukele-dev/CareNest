from rest_framework import serializers
from .models import Conversation, Message, UserOnlineStatus
from django.contrib.auth import get_user_model
from profiles.serializers import CaregiverProfileSerializer, ClientProfileSerializer

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    profile_type = serializers.CharField(source='user_type', read_only=True)
    display_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'profile_type', 'display_name', 'profile_picture']
    
    def get_display_name(self, obj):
        if obj.user_type == 'caregiver' and hasattr(obj, 'caregiver_profile'):
            return f"{obj.caregiver_profile.first_name} {obj.caregiver_profile.last_name}"
        elif obj.user_type == 'client' and hasattr(obj, 'client_profile'):
            return f"{obj.client_profile.first_name} {obj.client_profile.last_name}"
        return obj.email
    
    def get_profile_picture(self, obj):
        # You can add profile pictures later
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserBasicSerializer(source='sender', read_only=True)
    is_current_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_info', 'is_current_user',
            'content', 'is_read', 'read_at', 'booking', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_is_current_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserBasicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'other_user', 'last_message',
            'unread_count', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    
    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            other_user = obj.get_other_participant(request.user)
            if other_user:
                return UserBasicSerializer(other_user).data
        return None

class CreateMessageSerializer(serializers.Serializer):
    """Serializer for creating new messages"""
    content = serializers.CharField(max_length=2000)
    recipient_id = serializers.IntegerField(required=False)
    conversation_id = serializers.IntegerField(required=False)
    booking_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        request = self.context.get('request')
        
        # Either recipient_id or conversation_id must be provided
        if not data.get('recipient_id') and not data.get('conversation_id'):
            raise serializers.ValidationError(
                "Either recipient_id or conversation_id must be provided"
            )
        
        # Validate recipient exists
        if data.get('recipient_id'):
            try:
                recipient = User.objects.get(id=data['recipient_id'])
                data['recipient'] = recipient
            except User.DoesNotExist:
                raise serializers.ValidationError("Recipient not found")
        
        # Validate conversation exists (if provided)
        if data.get('conversation_id'):
            try:
                conversation = Conversation.objects.get(id=data['conversation_id'])
                if request.user not in conversation.participants.all():
                    raise serializers.ValidationError("You are not a participant in this conversation")
                data['conversation'] = conversation
            except Conversation.DoesNotExist:
                raise serializers.ValidationError("Conversation not found")
        
        return data

class OnlineStatusSerializer(serializers.ModelSerializer):
    user_info = UserBasicSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserOnlineStatus
        fields = ['user', 'user_info', 'is_online', 'last_seen']
        read_only_fields = ['last_seen']