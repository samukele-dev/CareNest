from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from profiles.models import CaregiverProfile, ClientProfile

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    # Relationships
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_bookings'
    )
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='caregiver_bookings'
    )
    
    # Booking details
    service_type = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=1)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    special_instructions = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Financials
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    caregiver_payout = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['caregiver', 'status']),
        ]
    
    def __str__(self):
        return f"Booking #{self.id}: {self.client.email} -> {self.caregiver.email}"
    
    def save(self, *args, **kwargs):
        # Calculate totals before saving
        if self.hours and self.hourly_rate and not self.total_amount:
            self.total_amount = self.hours * self.hourly_rate
            self.platform_fee = self.total_amount * 0.15  # 15% platform fee
            self.caregiver_payout = self.total_amount - self.platform_fee
        super().save(*args, **kwargs)

class BookingRequest(models.Model):
    """For booking requests that need caregiver confirmation"""
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_requests_sent'
    )
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_requests_received'
    )
    
    # Request details
    service_type = models.CharField(max_length=100)
    proposed_date = models.DateField()
    proposed_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=4)
    address = models.TextField()
    message = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Response
    caregiver_response = models.TextField(blank=True)
    proposed_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request #{self.id}: {self.client.email} -> {self.caregiver.email}"

class AvailabilitySlot(models.Model):
    """Caregiver availability slots"""
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_slots'
    )
    
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)
    specific_date = models.DateField(null=True, blank=True)  # For one-time slots
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['caregiver', 'day_of_week', 'start_time', 'specific_date']
    
    def __str__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f"{self.caregiver.email} - {days[self.day_of_week]} {self.start_time}-{self.end_time}"