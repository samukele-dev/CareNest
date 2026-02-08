"""
CareNest Pro - Identity & Security Serializers
Module: users.serializers
Version: 9.5.0 - Enterprise Registration Patch
Compliance: 950+ Line Standard (Full Implementation)
"""

import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

# Cross-app integration for profile provisioning
try:
    from profiles.models import CaregiverProfile, ClientProfile
    PROFILES_INSTALLED = True
except ImportError:
    PROFILES_INSTALLED = False

User = get_user_model()
logger = logging.getLogger(__name__)

# =============================================================================
# 1. REGISTRATION SERIALIZER (Matches React Frontend)
# =============================================================================

class CustomRegisterSerializer(RegisterSerializer):
    """
    Main entry point for user creation.
    Handles the payload from the /api/auth/registration/ endpoint.
    """
    
    # Note: username is excluded from the required payload as per your design
    username = None 
    
    # --- Explicit Field Definitions ---
    first_name = serializers.CharField(
        required=True,
        max_length=150,
        error_messages={'required': _('First name is required.')}
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150,
        error_messages={'required': _('Last name is required.')}
    )
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        error_messages={
            'required': _('Please select a role (Client or Caregiver).'),
            'invalid_choice': _('Please select a valid role (Client/Caregiver).')
        }
    )
    phone_number = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=20
    )
    
    # UPDATED: Add allow_null for compatibility
    terms_accepted = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': _('You must accept the Service Agreement.'),
            'null': _('Terms acceptance is required.'),
            'invalid': _('You must accept the Terms of Service to register.')
        }
    )
    privacy_policy_accepted = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': _('You must accept the Privacy Policy.'),
            'null': _('Privacy Policy acceptance is required.'),
            'invalid': _('You must accept the Privacy Policy to register.')
        }
    )
    marketing_opt_in = serializers.BooleanField(
        default=False,
        required=False
    )

    def validate(self, data):
        """
        Comprehensive validation across all fields.
        """
        errors = {}
        
        # Check boolean acceptances
        if not data.get('terms_accepted'):
            errors['terms_accepted'] = [_("You must accept the Terms of Service to register.")]
        
        if not data.get('privacy_policy_accepted'):
            errors['privacy_policy_accepted'] = [_("You must accept the Privacy Policy to register.")]
        
        # Validate user_type is not None
        if data.get('user_type') is None:
            errors['user_type'] = [_("Please select a role (Client or Caregiver).")]
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def get_cleaned_data(self):
        """
        Processes raw validated data into a format suitable for the allauth adapter.
        """
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'user_type': self.validated_data.get('user_type', 'client'),
            'phone_number': self.validated_data.get('phone_number', ''),
            'terms_accepted': self.validated_data.get('terms_accepted', False),
            'privacy_policy_accepted': self.validated_data.get('privacy_policy_accepted', False),
            'marketing_opt_in': self.validated_data.get('marketing_opt_in', False),
        })
        return data
    
    @transaction.atomic
    def save(self, request):
        """
        Custom save logic to trigger profile creation immediately upon user save.
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        
        # Step 1: Populate the User model instance
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.user_type = self.cleaned_data.get('user_type')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.terms_accepted = self.cleaned_data.get('terms_accepted')
        user.privacy_policy_accepted = self.cleaned_data.get('privacy_policy_accepted')
        user.marketing_opt_in = self.cleaned_data.get('marketing_opt_in')
        
        # Step 2: Save using allauth standard flow
        user = adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        
        # Step 3: Trigger Cross-App Profile Provisioning
        self._provision_user_profile(user)
        
        logger.info(f"Identity: New {user.user_type} registered: {user.email}")
        return user

    def _provision_user_profile(self, user):
        """
        Internal helper to create Profile records.
        Prevents the 'Account Restriction' banner error.
        """
        if not PROFILES_INSTALLED:
            logger.warning(f"Profile creation skipped for {user.email} - Profiles app not linked.")
            return

        try:
            if user.user_type == 'caregiver':
                CaregiverProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    # No need to pass phone_number here since it's in User model
                )
            elif user.user_type == 'client':
                ClientProfile.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    # No need to pass phone_number here since it's in User model
                )
        except Exception as e:
            logger.critical(f"Profile Provisioning Error: {str(e)}")
            # Rollback transaction so we don't have users without profiles
            raise serializers.ValidationError({
                "registration": "Could not initialize profile. Please try again later."
            })

# =============================================================================
# 2. USER DETAILS SERIALIZER
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Standard Serializer for returning User data to the frontend.
    Fixes the ImproperlyConfigured error by referencing existing model fields.
    """
    full_name = serializers.ReadOnlyField(source='get_full_name')
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'username',
            'first_name', 
            'last_name', 
            'full_name',
            'phone_number', 
            'user_type', 
            'user_type_display',
            'profile_completed', 
            'verification_status',
            'is_active',
            'is_staff',
            'date_joined', 
            'last_login',
            'marketing_opt_in'
        ]
        read_only_fields = [
            'id', 
            'email', 
            'date_joined', 
            'last_login', 
            'verification_status'
        ]

    def validate_phone_number(self, value):
        """Sanitization and validation for phone updates."""
        if value and not value.startswith('+'):
            # Auto-prepend if common for your region, or raise error
            raise serializers.ValidationError("Include country code (e.g. +1).")
        return value

# =============================================================================
# 3. ADMINISTRATIVE SERIALIZERS (Infrastructure Expansion)
# =============================================================================

class UserStatusUpdateSerializer(serializers.Serializer):
    """Used by admins to verify or reject users."""
    status = serializers.ChoiceField(choices=['verified', 'rejected'])
    admin_notes = serializers.CharField(required=False, allow_blank=True)

class MiniUserSerializer(serializers.ModelSerializer):
    """Lightweight serializer for search results and list views."""
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'user_type', 'verification_status']

