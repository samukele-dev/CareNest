# notifications/utils.py
from django.utils import timezone
from .models import Notification

class NotificationService:
    def send_new_message_notification(self, user, context):
        """Send notification for new message"""
        sender_name = context.get('sender_name', 'Someone')
        message_preview = context.get('message_preview', '')
        
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type='message',
                title=f"New message from {sender_name}",
                message=f"{sender_name}: {message_preview}",
                related_object_type='conversation',
                related_object_id=context.get('conversation_id')
            )
            print(f"✓ Notification sent to {user.email}: {notification.title}")
            return notification
        except Exception as e:
            print(f"✗ Failed to send notification: {e}")
            return None