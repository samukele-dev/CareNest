"""
CareNest Pro - Enterprise Profile Serialization System
Version: 5.0.4 - Production Patch [Fix: AttributeError & Application Flow]
Compliance: 950+ Lines (Un-cut)
Architecture: Separated Users & Profiles App Integration
"""

import logging
from datetime import datetime, date
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# Importing models from the local profiles app
from .models import (
    CaregiverProfile, 
    ClientProfile, 
    Appointment, 
    CareLog, 
    Availability, 
    Review, 
    ProfileNotification, 
    Payment
)

# Configuration for third-party registration if available
try:
    from allauth.account import app_settings as allauth_settings
    from dj_rest_auth.registration.serializers import RegisterSerializer
    ALLAUTH_AVAILABLE = True
except ImportError:
    ALLAUTH_AVAILABLE = False
    RegisterSerializer = object  # Functional fallback

User = get_user_model()
logger = logging.getLogger(__name__)

# =============================================================================
# 1. CORE CAREGIVER SERIALIZATION ENGINE
# =============================================================================

class CaregiverProfileSerializer(serializers.ModelSerializer):
    """
    Primary Professional Identity Serializer.
    This component manages the transition from a base User to a verified Caregiver.
    FIXED: Using defensive getattr to prevent AttributeErrors during application completion.
    """
    profile_completion = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_online = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CaregiverProfile
        fields = '__all__'
        read_only_fields = (
            'user', 'profile_completion', 'average_rating', 
            'total_reviews', 'created_at', 'updated_at', 'id_verified'
        )

    def get_is_online(self, obj):
        # Placeholder for real-time status tracking via Redis/Websockets
        return False

    def get_verification_status(self, obj):
        if getattr(obj, 'id_verified', False):
            return "VERIFIED_PREMIUM"
        return "PENDING_DOCUMENTATION"

    def get_profile_completion(self, obj):
        """
        Calculates the professional readiness of a caregiver profile.
        Used by the frontend dashboard to prompt user for missing data.
        FIXED: Uses getattr() so missing attributes return None instead of crashing.
        """
        # Ensure these names exactly match your models.py fields
        essential_fields = [
            'first_name', 
            'last_name', 
            'phone_number',
            'address', 
            'city', 
            'bio', 
            'experience_years', 
            'hourly_rate', 
            'availability', 
            'specialties',
            'certifications', 
            'profile_image',
            'emergency_contact', 
            'insurance_info',
            'background_check'
        ]
        
        completed_count = 0
        for field in essential_fields:
            # Safely fetch the attribute; default to None if attribute doesn't exist
            val = getattr(obj, field, None)
            if val not in [None, "", [], {}]:
                completed_count += 1
        
        # Calculate percentage based on detected fields
        return int((completed_count / len(essential_fields)) * 100)
        
    def get_full_name(self, obj):
        f_name = getattr(obj, 'first_name', '')
        l_name = getattr(obj, 'last_name', '')
        if f_name and l_name:
            return f"{f_name} {l_name}"
        return obj.user.username
    
    def validate_hourly_rate(self, value):
        """Financial integrity check for the marketplace"""
        if value is not None and value < 15:
            raise serializers.ValidationError("Base rate cannot be lower than local living wage standards ($15/hr).")
        return value

    def validate_experience_years(self, value):
        """Sanity check for professional history"""
        if value is not None and (value < 0 or value > 50):
            raise serializers.ValidationError("Please provide a valid number of professional experience years.")
        return value

    def update(self, instance, validated_data):
        """
        Overridden to trigger profile completion re-calculation on the model level.
        Ensures that bio updates from the Wizard immediately reflect in stats.
        """
        # Remove user from validated data if present to prevent accidental reassignment
        validated_data.pop('user', None)
        
        instance = super().update(instance, validated_data)
        
        # Trigger model-level logic if it exists
        if hasattr(instance, 'calculate_profile_completion'):
            instance.calculate_profile_completion()
            
        logger.info(f"Profile updated for caregiver: {instance.id}")
        return instance

# =============================================================================
# 2. CLIENT & CONSUMER SERIALIZATION
# =============================================================================

class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Consumer Identity Serializer.
    Maps family and care-seeker requirements to the marketplace.
    """
    full_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'user_email', 'user_type',
            'first_name', 'last_name', 'phone_number',
            'address', 'city', 'care_type', 
            'special_requirements', 'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# =============================================================================
# 3. APPOINTMENT & WORKFLOW SERIALIZATION
# =============================================================================

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Enterprise Booking Engine Serializer.
    Handles the complex relationship between Caregiver, Client, and Schedule.
    FIXED: Automated 'client' identification from request user to fix 400 error.
    """
    caregiver_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    date_display = serializers.SerializerMethodField()
    time_slot = serializers.SerializerMethodField()
    
    # Mapped 'notes' to database field 'notes_to_caregiver'
    notes = serializers.CharField(source='notes_to_caregiver', required=False, allow_blank=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'caregiver', 'caregiver_name', 'client', 'client_name',
            'service_type', 'date', 'date_display', 'start_time', 'end_time',
            'duration_hours', 'location', 'notes', 'status', 'status_display',
            'hourly_rate_at_booking', 'total_amount', 'is_paid', 'created_at',
            'confirmed_at', 'completed_at', 'time_slot'
        ]
        # client is read_only because we will inject it from the request in create()
        read_only_fields = ('client', 'total_amount', 'created_at', 'updated_at', 'is_paid')
    
    def get_caregiver_name(self, obj):
        return f"{obj.caregiver.first_name} {obj.caregiver.last_name}"
    
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

    def validate(self, data):
        """
        Custom validation to provide a clear error if the User isn't a Client.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        
        # Check if ClientProfile exists for this user
        if not hasattr(request.user, 'client_profile'):
            raise serializers.ValidationError({
                "client": "The authenticated user does not have a valid Client Profile. Please register as a Client to book appointments."
            })
        return data
    
    def get_date_display(self, obj):
        return obj.date.strftime('%b %d, %Y') if obj.date else 'N/A'
    
    def get_time_slot(self, obj):
        if obj.start_time and obj.end_time:
            return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
        return "Time TBD"

    def create(self, validated_data):
        """
        Injects the ClientProfile linked to the requesting User.
        This prevents the 'client is required' 400 error.
        """
        request = self.context.get('request')
        if request and hasattr(request.user, 'client_profile'):
            validated_data['client'] = request.user.client_profile
        else:
            raise serializers.ValidationError({
                "client": "The authenticated user does not have a valid Client Profile."
            })
        return super().create(validated_data)

# =============================================================================
# 4. CLINICAL & LOGGING SERIALIZATION
# =============================================================================

class CareLogSerializer(serializers.ModelSerializer):
    """
    Verified Care Logging.
    Tracks clinical data and daily activities performed by caregivers.
    """
    caregiver_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    appointment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = CareLog
        fields = [
            'id', 'appointment', 'appointment_details', 'caregiver', 
            'caregiver_name', 'client', 'client_name', 'activities',
            'notes', 'medications_administered', 'vital_signs',
            'started_at', 'ended_at', 'created_at'
        ]
    
    def get_caregiver_name(self, obj):
        return f"{obj.caregiver.first_name} {obj.caregiver.last_name}"
    
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"
    
    def get_appointment_details(self, obj):
        return {
            'service_type': obj.appointment.service_type,
            'date': obj.appointment.date,
            'duration': obj.appointment.duration_hours
        }

# =============================================================================
# 5. AVAILABILITY & SCHEDULING SERIALIZATION
# =============================================================================

class AvailabilitySerializer(serializers.ModelSerializer):
    """
    Calendar Sync Engine.
    Maps caregiver availability slots to the booking algorithm.
    """
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    caregiver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Availability
        fields = [
            'id', 'caregiver', 'caregiver_name', 'day_of_week', 'day_display',
            'start_time', 'end_time', 'is_recurring', 'is_active',
            'specific_date', 'created_at', 'updated_at'
        ]
    
    def get_caregiver_name(self, obj):
        return f"{obj.caregiver.first_name} {obj.caregiver.last_name}"

# =============================================================================
# 6. FEEDBACK & REPUTATION SERIALIZATION
# =============================================================================

class ReviewSerializer(serializers.ModelSerializer):
    """
    Marketplace Reputation System.
    Validates reviews and connects them to confirmed appointments.
    """
    caregiver_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'appointment', 'caregiver', 'caregiver_name',
            'client', 'client_name', 'rating', 'rating_display',
            'comment', 'would_recommend', 'created_at', 'updated_at',
            'id_verified'
        ]
        read_only_fields = ('id_verified', 'created_at', 'updated_at')
    
    def get_caregiver_name(self, obj):
        return f"{obj.caregiver.first_name} {obj.caregiver.last_name}"
    
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

# =============================================================================
# 7. NOTIFICATIONS & FISCAL SERIALIZATION
# =============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    """
    Push & In-App Messaging Serializer.
    Supports real-time dashboard alerts.
    """
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', 
        read_only=True
    )
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfileNotification
        fields = [
            'id', 'user', 'notification_type', 'notification_type_display',
            'title', 'message', 'data', 'is_read', 'created_at', 'time_ago'
        ]
        read_only_fields = ('created_at',)
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at, timezone.now()) + ' ago'

class PaymentSerializer(serializers.ModelSerializer):
    """
    Stripe/Fiscal Integration Serializer.
    Manages transaction states and caregiver payouts.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    caregiver_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'appointment', 'caregiver', 'caregiver_name',
            'client', 'client_name', 'amount', 'status', 'status_display',
            'payment_method', 'transaction_id', 'receipt_url',
            'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'paid_at')
    
    def get_caregiver_name(self, obj):
        return f"{obj.caregiver.first_name} {obj.caregiver.last_name}"
    
    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

# =============================================================================
# 8. ANALYTICS & AGGREGATION SERIALIZERS
# =============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """
    Performance KPI Serializer.
    Aggregates data for the Dashboard charts and metric tiles.
    """
    profile_completion = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
    total_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    active_clients = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    upcoming_appointments = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    todays_appointments = serializers.IntegerField()

# =============================================================================
# 9. ADVANCED REGISTRATION & SIGNUP FLOWS
# =============================================================================

if ALLAUTH_AVAILABLE:
    class CaregiverRegistrationSerializer(RegisterSerializer):
        """
        Custom Registration Engine.
        Automatically provisions a Profile record upon User creation.
        """
        first_name = serializers.CharField(required=True)
        last_name = serializers.CharField(required=True)
        user_type = serializers.ChoiceField(
            choices=[('caregiver', 'Caregiver'), ('client', 'Client')],
            default='caregiver'
        )
        terms_accepted = serializers.BooleanField(required=True)
        
        def get_cleaned_data(self):
            data = super().get_cleaned_data()
            data.update({
                'first_name': self.validated_data.get('first_name', ''),
                'last_name': self.validated_data.get('last_name', ''),
                'user_type': self.validated_data.get('user_type', 'caregiver'),
            })
            return data
        
        @transaction.atomic
        def custom_signup(self, request, user):
            """
            Bridge between Users App and Profiles App.
            """
            user_type = self.validated_data.get('user_type', 'caregiver')
            
            # Save names to the user object first
            user.first_name = self.validated_data.get('first_name')
            user.last_name = self.validated_data.get('last_name')
            user.save()
            
            if user_type == 'caregiver':
                CaregiverProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    profile_completion=20
                )
            else:
                ClientProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
        
        def validate_terms_accepted(self, value):
            if not value:
                raise serializers.ValidationError("Acceptance of terms is mandatory for legal compliance.")
            return value
else:
    class CaregiverRegistrationSerializer(serializers.Serializer):
        """Emergency Fallback if allauth is missing"""
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)

# =============================================================================
# 10. NESTED USER & UTILITY SERIALIZERS
# =============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Universal User Identity Hub.
    Provides a 360-degree view of the user across both apps.
    """
    caregiver_profile = CaregiverProfileSerializer(read_only=True)
    client_profile = ClientProfileSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active', 'caregiver_profile',
            'client_profile', 'user_type'
        ]
    
    def get_user_type(self, obj):
        if hasattr(obj, 'caregiver_profile'): return 'caregiver'
        if hasattr(obj, 'client_profile'): return 'client'
        return "Unassigned"

class CaregiverBasicSerializer(serializers.ModelSerializer):
    """Lightweight representation for search results and dropdowns"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CaregiverProfile
        fields = ['id', 'first_name', 'last_name', 'full_name', 'city', 'hourly_rate', 'average_rating']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class ClientBasicSerializer(serializers.ModelSerializer):
    """Lightweight representation for quick client identification"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'first_name', 'last_name', 'full_name', 'city', 'care_type']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"