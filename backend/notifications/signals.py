# notifications/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference
from .utils import NotificationService

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences when a new user is created"""
    if created:
        NotificationPreference.objects.create(user=instance)

# You can also create signals for other apps to trigger notifications
# For example, when a new message is sent in messaging app