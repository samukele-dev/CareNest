from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class CaregiverProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='caregiver_profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ])
    
    # Professional Information
    years_experience = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    bio = models.TextField(blank=True)
    
    # Skills & Services
    skills = models.JSONField(default=list, blank=True)  # ['elderly_care', 'child_care', 'disabled_care']
    certifications = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)  # ['English', 'Zulu', 'Afrikaans']
    
    # Availability
    is_available = models.BooleanField(default=True)
    available_days = models.JSONField(default=list, blank=True)  # ['monday', 'tuesday', ...]
    available_times = models.CharField(max_length=100, blank=True)  # '9am-5pm'
    
    # Location
    city = models.CharField(max_length=100)
    suburb = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Verification
    id_verified = models.BooleanField(default=False)
    background_check = models.BooleanField(default=False)
    profile_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Status
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-profile_score', '-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"

class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Care needs
    care_type = models.CharField(max_length=50, choices=[
        ('elderly', 'Elderly Care'),
        ('child', 'Child Care'),
    ])
    special_requirements = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"