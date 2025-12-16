from rest_framework import serializers
from .models import CaregiverProfile, ClientProfile
from django.conf import settings

class CaregiverProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    class Meta:
        model = CaregiverProfile
        fields = [
            'id', 'email', 'user_type',
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'years_experience', 'hourly_rate', 'bio',
            'skills', 'certifications', 'languages',
            'is_available', 'available_days', 'available_times',
            'city', 'suburb', 'latitude', 'longitude',
            'id_verified', 'background_check', 'profile_score',
            'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_score']

class ClientProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'email', 'user_type',
            'first_name', 'last_name', 'phone_number',
            'address', 'city',
            'care_type', 'special_requirements',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']