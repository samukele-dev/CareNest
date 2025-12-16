from rest_framework import serializers
from .models import Booking, BookingRequest, AvailabilitySlot
from django.conf import settings
from profiles.serializers import CaregiverProfileSerializer, ClientProfileSerializer

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    caregiver_name = serializers.CharField(source='caregiver.caregiver_profile.first_name', read_only=True)
    
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'caregiver', 'caregiver_name',
            'day_of_week', 'start_time', 'end_time',
            'is_recurring', 'specific_date'
        ]
        read_only_fields = ['id']

class BookingRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_profile.first_name', read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.caregiver_profile.first_name', read_only=True)
    client_profile = ClientProfileSerializer(source='client.client_profile', read_only=True)
    
    class Meta:
        model = BookingRequest
        fields = [
            'id', 'client', 'client_name', 'client_profile',
            'caregiver', 'caregiver_name',
            'service_type', 'proposed_date', 'proposed_time', 'duration_hours',
            'address', 'message', 'status',
            'caregiver_response', 'proposed_rate',
            'created_at', 'updated_at', 'viewed_at', 'responded_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'viewed_at', 'responded_at']

class BookingSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_profile.first_name', read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.caregiver_profile.first_name', read_only=True)
    client_profile = ClientProfileSerializer(source='client.client_profile', read_only=True)
    caregiver_profile = CaregiverProfileSerializer(source='caregiver.caregiver_profile', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'client_name', 'client_profile',
            'caregiver', 'caregiver_name', 'caregiver_profile',
            'service_type', 'start_datetime', 'end_datetime', 'hours',
            'address', 'city', 'special_instructions',
            'status', 'payment_status',
            'hourly_rate', 'total_amount', 'platform_fee', 'caregiver_payout',
            'created_at', 'updated_at', 'confirmed_at', 'completed_at',
            'cancelled_at', 'cancellation_reason'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'confirmed_at', 
            'completed_at', 'cancelled_at', 'total_amount',
            'platform_fee', 'caregiver_payout'
        ]

class CreateBookingRequestSerializer(serializers.Serializer):
    """Serializer for creating booking requests"""
    caregiver_id = serializers.IntegerField()
    service_type = serializers.CharField(max_length=100)
    proposed_date = serializers.DateField()
    proposed_time = serializers.TimeField()
    duration_hours = serializers.DecimalField(max_digits=4, decimal_places=1, default=4)
    address = serializers.CharField()
    message = serializers.CharField(required=False, allow_blank=True)
    
    def validate_caregiver_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            caregiver = User.objects.get(id=value, user_type='caregiver')
            # Check if caregiver has a profile
            if not hasattr(caregiver, 'caregiver_profile'):
                raise serializers.ValidationError("Caregiver profile not found")
        except User.DoesNotExist:
            raise serializers.ValidationError("Caregiver not found")
        
        return value

class AcceptBookingRequestSerializer(serializers.Serializer):
    """Serializer for accepting booking requests"""
    accepted = serializers.BooleanField()
    proposed_rate = serializers.DecimalField(
        required=False, 
        max_digits=6, 
        decimal_places=2,
        allow_null=True
    )
    response_message = serializers.CharField(required=False, allow_blank=True)