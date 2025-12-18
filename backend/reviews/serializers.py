from rest_framework import serializers
from .models import Review
from profiles.serializers import CaregiverProfileSerializer
from bookings.serializers import BookingSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.client_profile.first_name', read_only=True)
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.caregiver_profile.first_name', read_only=True)
    caregiver_profile = CaregiverProfileSerializer(source='caregiver.caregiver_profile', read_only=True)
    booking_details = BookingSerializer(source='booking', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'booking_details',
            'reviewer', 'reviewer_name', 'reviewer_email',
            'caregiver', 'caregiver_name', 'caregiver_profile',
            'rating', 'comment', 'would_recommend',
            'caregiver_response', 'responded_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reviewer', 'caregiver', 'booking',
            'created_at', 'updated_at', 'responded_at',
            'reviewer_name', 'reviewer_email', 'caregiver_name'
        ]

class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'comment', 'would_recommend']
    
    def validate(self, data):
        request = self.context.get('request')
        booking = data['booking']
        
        # Check if user is the client for this booking
        if booking.client != request.user:
            raise serializers.ValidationError("You can only review your own bookings.")
        
        # Check if booking is completed
        if booking.status != 'completed':
            raise serializers.ValidationError("You can only review completed bookings.")
        
        # Check if review already exists
        if Review.objects.filter(booking=booking, reviewer=request.user).exists():
            raise serializers.ValidationError("You have already reviewed this booking.")
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        booking = validated_data['booking']
        
        review = Review.objects.create(
            booking=booking,
            reviewer=request.user,
            caregiver=booking.caregiver,
            rating=validated_data['rating'],
            comment=validated_data['comment'],
            would_recommend=validated_data['would_recommend']
        )
        
        # Update caregiver's average rating
        self.update_caregiver_rating(booking.caregiver)
        
        return review
    
    def update_caregiver_rating(self, caregiver):
        """Update caregiver's profile score based on reviews"""
        reviews = Review.objects.filter(caregiver=caregiver)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            # Update profile score (0-100 scale, rating * 20)
            caregiver.caregiver_profile.profile_score = min(100, avg_rating * 20)
            caregiver.caregiver_profile.save()

class CaregiverResponseSerializer(serializers.Serializer):
    response = serializers.CharField(max_length=1000)