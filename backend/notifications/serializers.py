# notifications/serializers.py
from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'read_at', 'created_at', 'time_ago',
            'related_object_id', 'related_object_type'
        ]
        read_only_fields = ['created_at', 'read_at']
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'email_notifications', 'push_notifications', 'updated_at']
        read_only_fields = ['updated_at']


class MarkAsReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)