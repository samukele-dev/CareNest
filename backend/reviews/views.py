from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model

from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer, CaregiverResponseSerializer
from bookings.models import Booking

User = get_user_model()

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for reviews"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'client':
            return Review.objects.filter(reviewer=user)
        elif user.user_type == 'caregiver':
            return Review.objects.filter(caregiver=user)
        else:  # admin
            return Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Caregiver responds to a review"""
        review = self.get_object()
        
        if review.caregiver != request.user:
            return Response(
                {"error": "Only the caregiver can respond to this review"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CaregiverResponseSerializer(data=request.data)
        if serializer.is_valid():
            review.caregiver_response = serializer.validated_data['response']
            review.responded_at = timezone.now()
            review.save()
            
            return Response(ReviewSerializer(review).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def caregiver_reviews(request, caregiver_id):
    """Get all reviews for a specific caregiver (public endpoint)"""
    try:
        caregiver = User.objects.get(id=caregiver_id, user_type='caregiver')
    except User.DoesNotExist:
        return Response(
            {"error": "Caregiver not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    reviews = Review.objects.filter(caregiver=caregiver).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    
    # Calculate stats
    stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        recommended=Count('id', filter=models.Q(would_recommend=True))
    )
    
    return Response({
        "caregiver_id": caregiver_id,
        "caregiver_name": caregiver.caregiver_profile.first_name if hasattr(caregiver, 'caregiver_profile') else "Unknown",
        "stats": stats,
        "reviews": serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_to_review(request):
    """Get bookings that are available for review by current user"""
    if request.user.user_type != 'client':
        return Response(
            {"error": "Only clients can review bookings"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get completed bookings that haven't been reviewed yet
    completed_bookings = Booking.objects.filter(
        client=request.user,
        status='completed'
    )
    
    reviewed_bookings = Review.objects.filter(
        reviewer=request.user
    ).values_list('booking_id', flat=True)
    
    available_bookings = completed_bookings.exclude(id__in=reviewed_bookings)
    
    from bookings.serializers import BookingSerializer
    serializer = BookingSerializer(available_bookings, many=True)
    
    return Response({
        "available_count": available_bookings.count(),
        "bookings": serializer.data
    })

class ReviewStatsView(generics.RetrieveAPIView):
    """Get review statistics for a caregiver"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, caregiver_id):
        try:
            caregiver = User.objects.get(id=caregiver_id, user_type='caregiver')
        except User.DoesNotExist:
            return Response(
                {"error": "Caregiver not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reviews = Review.objects.filter(caregiver=caregiver)
        
        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
            five_star=Count('id', filter=models.Q(rating=5)),
            four_star=Count('id', filter=models.Q(rating=4)),
            three_star=Count('id', filter=models.Q(rating=3)),
            two_star=Count('id', filter=models.Q(rating=2)),
            one_star=Count('id', filter=models.Q(rating=1)),
            recommended=Count('id', filter=models.Q(would_recommend=True))
        )
        
        # Calculate percentages
        total = stats['total_reviews'] or 1  # Avoid division by zero
        stats['recommendation_rate'] = round((stats['recommended'] / total) * 100, 1) if total > 0 else 0
        stats['response_rate'] = round((reviews.filter(caregiver_response__isnull=False).count() / total) * 100, 1) if total > 0 else 0
        
        return Response(stats)