# notifications/views.py
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    MarkAsReadSerializer
)

User = get_user_model()

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notifications (read-only)"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user)
        
        # Filter by read status
        is_read = self.request.query_params.get('read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Filter by type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark notifications as read"""
        serializer = MarkAsReadSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('mark_all', False):
                # Mark all notifications as read
                updated = Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                return Response({"marked_read": updated})
            else:
                # Mark specific notifications as read
                notification_ids = data.get('notification_ids', [])
                if notification_ids:
                    updated = Notification.objects.filter(
                        user=request.user,
                        id__in=notification_ids,
                        is_read=False
                    ).update(
                        is_read=True,
                        read_at=timezone.now()
                    )
                    return Response({"marked_read": updated})
                else:
                    return Response(
                        {"error": "Either provide notification_ids or set mark_all=true"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({"unread_count": count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark single notification as read"""
        notification = self.get_object()
        if not notification.is_read:
            notification.mark_as_read()
        return Response({"status": "marked as read"})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create preferences for user"""
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Simple utility view to create notifications
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_notification(request):
    """Create a notification for current user or another user"""
    user_id = request.data.get('user_id')
    title = request.data.get('title', 'Notification')
    message = request.data.get('message', '')
    notification_type = request.data.get('type', 'system')
    
    # Determine target user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = request.user
    
    # Create notification
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=request.data.get('related_object_id'),
        related_object_type=request.data.get('related_object_type')
    )
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Test endpoint
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_notification(request):
    """Send a test notification to current user"""
    notification = Notification.objects.create(
        user=request.user,
        notification_type='system',
        title='Test Notification',
        message='This is a test notification to verify the system is working.'
    )
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)