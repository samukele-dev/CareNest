"""
CareNest Pro - Enterprise Database Schema
Version: 4.0.0
Author: Gemini Thought Partner
Description: Professional-grade Django models for a multi-tenant caregiver marketplace.
Includes: Caregiver/Client Profiles, Appointment Scheduling, Real-time Notifications, 
Care Logs, and Transactional Payment Tracking.
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count
from decimal import Decimal

User = get_user_model()

# =============================================================================
# ENUMERATIONS & CHOICES
# =============================================================================

class AppointmentStatus(models.TextChoices):
    PENDING = 'pending', _('Pending Approval')
    CONFIRMED = 'confirmed', _('Confirmed')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')
    NO_SHOW = 'no_show', _('No Show')
    EXPIRED = 'expired', _('Expired Request')

class NotificationType(models.TextChoices):
    APPOINTMENT_REQUEST = 'appointment_request', _('Appointment Request')
    APPOINTMENT_CONFIRMED = 'appointment_confirmed', _('Appointment Confirmed')
    APPOINTMENT_CANCELLED = 'appointment_cancelled', _('Appointment Cancelled')
    MESSAGE = 'message', _('New Message')
    REVIEW = 'review', _('New Review')
    PAYMENT = 'payment', _('Payment Received')
    SYSTEM = 'system', _('System Alert')
    SECURITY = 'security', _('Security Alert')

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    REFUNDED = 'refunded', _('Refunded')
    DISPUTED = 'disputed', _('Disputed')

class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, _('Monday')
    TUESDAY = 1, _('Tuesday')
    WEDNESDAY = 2, _('Wednesday')
    THURSDAY = 3, _('Thursday')
    FRIDAY = 4, _('Friday')
    SATURDAY = 5, _('Saturday')
    SUNDAY = 6, _('Sunday')

# =============================================================================
# 1. CAREGIVER PROFILE
# =============================================================================

class CaregiverProfile(models.Model):
    """
    Main identity model for caregivers. 
    Includes professional bio, verification status, and fiscal settings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='caregiver_profile'
    )
    
    # Personal Info
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(
        blank=True, 
        null=True, 
        help_text=_("Professional summary for the marketplace.")
    )
    
    # Professional Metrics
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=25.00,
        validators=[MinValueValidator(Decimal('15.00'))]
    )
    experience_years = models.PositiveIntegerField(default=1)
    specialties = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("List of care types (e.g. Elderly, Childcare, Post-Op)")
    )
    
    # Location Data
    location = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Verification & Trust
    is_featured = models.BooleanField(default=False)
    background_check_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    
    # Assets
    profile_image = models.ImageField(upload_to='caregiver_profiles/avatars/', null=True, blank=True)
    id_document = models.FileField(upload_to='caregiver_profiles/documents/', null=True, blank=True)
    
    # Aggregate Stats
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    profile_completion_percentage = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_as_caregiver = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Caregiver Profile")
        verbose_name_plural = _("Caregiver Profiles")
        ordering = ['-average_rating', '-created_at']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.username

    def update_rating(self):
        """Recalculate average rating based on Review model."""
        stats = self.reviews.filter(is_visible=True).aggregate(
            avg=Avg('rating'), 
            count=Count('id')
        )
        self.average_rating = stats['avg'] or 0.00
        self.total_reviews = stats['count'] or 0
        self.save()

# =============================================================================
# 2. CLIENT PROFILE
# =============================================================================

class ClientProfile(models.Model):
    """
    Identity model for families or individuals seeking care.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_profile'
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    
    # Logistics
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=25, blank=True, null=True)
    
    # Preferences
    preferred_care_type = models.CharField(max_length=100, blank=True, null=True)
    special_requirements = models.TextField(
        blank=True, 
        null=True, 
        help_text=_("Medical conditions, dietary restrictions, etc.")
    )
    
    # Metadata
    is_premium_member = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client: {self.first_name} {self.last_name}" if self.first_name else self.user.username

# =============================================================================
# 3. APPOINTMENT (CORE ENGINE)
# =============================================================================

class Appointment(models.Model):
    """
    Records a scheduled care session between caregiver and client.
    """
    caregiver = models.ForeignKey(
        CaregiverProfile, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    client = models.ForeignKey(
        ClientProfile, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    
    # Schedule
    service_type = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('1.0')  # Use Decimal for default
    )
    
    # Physical Location
    location = models.CharField(max_length=255, blank=True, null=True)
    notes_to_caregiver = models.TextField(blank=True, null=True)
    
    # Financials
    hourly_rate_at_booking = models.DecimalField(
        max_digits=8, 
        decimal_places=2
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')  # Use Decimal for default
    )
    is_paid = models.BooleanField(default=False)
    
    # Lifecycle
    status = models.CharField(
        max_length=25, 
        choices=AppointmentStatus.choices, 
        default=AppointmentStatus.PENDING
    )
    
    # Audit Trail
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total based on rate and duration
        from decimal import Decimal
        
        # Ensure duration_hours is Decimal
        if self.duration_hours and not isinstance(self.duration_hours, Decimal):
            self.duration_hours = Decimal(str(self.duration_hours))
        
        # Ensure hourly_rate_at_booking is Decimal
        if self.hourly_rate_at_booking and not isinstance(self.hourly_rate_at_booking, Decimal):
            self.hourly_rate_at_booking = Decimal(str(self.hourly_rate_at_booking))
        
        # Calculate total if we have both values
        if self.duration_hours and self.hourly_rate_at_booking:
            self.total_amount = self.duration_hours * self.hourly_rate_at_booking
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Apt #{self.id} | {self.date} | {self.status}"


# =============================================================================
# 4. AVAILABILITY SYNC
# =============================================================================

class Availability(models.Model):
    """
    Recurring or specific time slots where a caregiver is available.
    """
    caregiver = models.ForeignKey(
        CaregiverProfile, 
        on_delete=models.CASCADE, 
        related_name='availabilities'
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices, null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True, help_text=_("For one-off availability."))
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Availabilities"

# =============================================================================
# 5. ENTERPRISE REVIEWS
# =============================================================================

class Review(models.Model):
    """
    Feedback loop for clients to rate caregivers after an appointment.
    """
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='review'
    )
    caregiver = models.ForeignKey(
        CaregiverProfile, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    client = models.ForeignKey(
        ClientProfile, 
        on_delete=models.CASCADE, 
        related_name='reviews_given'
    )
    
    rating = models.IntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    
    # Visibility controls
    is_visible = models.BooleanField(default=True)
    caregiver_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Trigger aggregate update on profile
        self.caregiver.update_rating()

# =============================================================================
# 6. NOTIFICATION SYSTEM
# =============================================================================

class ProfileNotification(models.Model):
    """
    Internal notification bus for UI alerts.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile_notifications'
    )
    notification_type = models.CharField(
        max_length=50, 
        choices=NotificationType.choices, 
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Store relevant IDs for frontend routing (e.g. {"appointment_id": 42})
    data = models.JSONField(default=dict, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# =============================================================================
# 7. MEDICAL CARE LOGS
# =============================================================================

class CareLog(models.Model):
    """
    Clinical or daily activity log filled by caregiver during an appointment.
    """
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='care_log'
    )
    caregiver = models.ForeignKey(CaregiverProfile, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    
    # Dynamic Fields
    activities_performed = models.JSONField(default=list, blank=True)
    medications_given = models.JSONField(default=list, blank=True)
    vitals_recorded = models.JSONField(default=dict, blank=True)
    
    # Narrative
    detailed_notes = models.TextField(blank=True)
    incident_reports = models.TextField(blank=True, null=True)
    
    # Timestamping for Shift
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# =============================================================================
# 8. FINANCIAL TRANSACTIONS
# =============================================================================

class Payment(models.Model):
    """
    Financial record of transactions within the platform.
    """
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='payments'
    )
    caregiver = models.ForeignKey(CaregiverProfile, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_to_caregiver = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField(
        max_length=25, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.uuid} - {self.status}"

# =============================================================================
# 9. ATTACHMENT GALLERY (EXTENSION)
# =============================================================================

class ProfileAttachment(models.Model):
    """Gallery for caregiver certifications and awards."""
    caregiver = models.ForeignKey(
        CaregiverProfile, 
        on_delete=models.CASCADE, 
        related_name='certifications'
    )
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='caregiver_profiles/certs/')
    is_verified = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)