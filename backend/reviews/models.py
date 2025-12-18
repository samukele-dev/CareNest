# reviews/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review'
    )
    
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    would_recommend = models.BooleanField(default=True)
    
    # Response from caregiver
    caregiver_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['booking', 'reviewer']
    
    def __str__(self):
        return f"Review #{self.id}: {self.rating} stars"