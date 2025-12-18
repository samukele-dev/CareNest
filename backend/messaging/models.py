from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversation(models.Model):
    """A conversation between two users"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = [user.email for user in self.participants.all()[:2]]
        return f"Conversation: {' & '.join(participant_names)}"
    
    def get_other_participant(self, user):
        """Get the other user in the conversation"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    
    # Message status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Message about a booking
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email}: {self.content[:50]}..."
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class UserOnlineStatus(models.Model):
    """Track user online status for messaging"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='online_status'
    )
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {'Online' if self.is_online else 'Offline'}"