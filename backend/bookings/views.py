from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import json

from .models import Booking, BookingRequest, AvailabilitySlot
from .serializers import (
    BookingSerializer, BookingRequestSerializer, AvailabilitySlotSerializer,
    CreateBookingRequestSerializer, AcceptBookingRequestSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for bookings"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'client':
            return Booking.objects.filter(client=user)
        elif user.user_type == 'caregiver':
            return Booking.objects.filter(caregiver=user)
        else:  # admin
            return Booking.objects.all()
    
    def perform_create(self, serializer):
        # Only caregivers can create bookings directly
        if self.request.user.user_type == 'caregiver':
            serializer.save(caregiver=self.request.user)
        else:
            serializer.save(client=self.request.user)

class BookingRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for booking requests"""
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'client':
            return BookingRequest.objects.filter(client=user)
        elif user.user_type == 'caregiver':
            return BookingRequest.objects.filter(caregiver=user)
        else:  # admin
            return BookingRequest.objects.all()
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept or reject a booking request"""
        booking_request = self.get_object()
        
        if booking_request.caregiver != request.user:
            return Response(
                {"error": "Only the caregiver can respond to this request"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AcceptBookingRequestSerializer(data=request.data)
        if serializer.is_valid():
            accepted = serializer.validated_data['accepted']
            proposed_rate = serializer.validated_data.get('proposed_rate')
            response_message = serializer.validated_data.get('response_message', '')
            
            if accepted:
                booking_request.status = 'accepted'
                booking_request.caregiver_response = response_message
                if proposed_rate:
                    booking_request.proposed_rate = proposed_rate
                
                # Create booking from accepted request
                start_datetime = timezone.make_aware(
                    datetime.combine(booking_request.proposed_date, booking_request.proposed_time)
                )
                end_datetime = start_datetime + timedelta(hours=float(booking_request.duration_hours))
                
                # Get city from client profile or use default
                city = "Unknown"
                if hasattr(booking_request.client, 'client_profile') and booking_request.client.client_profile.city:
                    city = booking_request.client.client_profile.city
                
                # Get hourly rate
                hourly_rate = proposed_rate
                if not hourly_rate and hasattr(booking_request.caregiver, 'caregiver_profile'):
                    hourly_rate = booking_request.caregiver.caregiver_profile.hourly_rate
                
                Booking.objects.create(
                    client=booking_request.client,
                    caregiver=booking_request.caregiver,
                    service_type=booking_request.service_type,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    hours=booking_request.duration_hours,
                    address=booking_request.address,
                    city=city,
                    hourly_rate=hourly_rate or 0,
                    status='confirmed',
                    confirmed_at=timezone.now()
                )
            else:
                booking_request.status = 'rejected'
                booking_request.caregiver_response = response_message or 'Request rejected'
            
            booking_request.responded_at = timezone.now()
            booking_request.save()
            
            return Response(self.get_serializer(booking_request).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_booking_request(request):
    """Create a new booking request (client sends to caregiver)"""
    if request.user.user_type != 'client':
        return Response(
            {"error": "Only clients can create booking requests"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CreateBookingRequestSerializer(data=request.data)
    if serializer.is_valid():
        caregiver = User.objects.get(id=serializer.validated_data['caregiver_id'])
        
        # Check if caregiver is available
        if not caregiver.caregiver_profile.is_available:
            return Response(
                {"error": "Caregiver is not currently available"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking_request = BookingRequest.objects.create(
            client=request.user,
            caregiver=caregiver,
            service_type=serializer.validated_data['service_type'],
            proposed_date=serializer.validated_data['proposed_date'],
            proposed_time=serializer.validated_data['proposed_time'],
            duration_hours=serializer.validated_data['duration_hours'],
            address=serializer.validated_data['address'],
            message=serializer.validated_data.get('message', ''),
            expires_at=timezone.now() + timedelta(hours=48)  # 48 hours to respond
        )
        
        return Response(
            BookingRequestSerializer(booking_request).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_caregiver_availability(request, caregiver_id):
    """Check caregiver availability for a specific date/time"""
    try:
        caregiver = User.objects.get(id=caregiver_id, user_type='caregiver')
    except User.DoesNotExist:
        return Response(
            {"error": "Caregiver not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    date_str = request.query_params.get('date')
    time_str = request.query_params.get('time')
    
    if not date_str or not time_str:
        return Response(
            {"error": "Date and time parameters required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        check_time = datetime.strptime(time_str, '%H:%M').time()
        check_datetime = timezone.make_aware(datetime.combine(check_date, check_time))
    except ValueError:
        return Response(
            {"error": "Invalid date or time format. Use YYYY-MM-DD and HH:MM"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if caregiver is generally available
    if not caregiver.caregiver_profile.is_available:
        return Response({
            "available": False,
            "reason": "Caregiver is not currently accepting bookings"
        })
    
    # Check for existing bookings at that time
    day_of_week = check_date.weekday()
    
    # Check availability slots

    availability_slots = AvailabilitySlot.objects.filter(
        Q(caregiver=caregiver, specific_date=check_date) |
        Q(caregiver=caregiver, is_recurring=True, day_of_week=day_of_week)
    )
    
    is_available = availability_slots.filter(
        start_time__lte=check_time,
        end_time__gte=check_time
    ).exists()
    
    # Check for conflicting bookings
    conflicting_bookings = Booking.objects.filter(
        caregiver=caregiver,
        status__in=['confirmed', 'in_progress'],
        start_datetime__lt=check_datetime + timedelta(hours=1),
        end_datetime__gt=check_datetime - timedelta(hours=1)
    ).exists()
    
    if conflicting_bookings:
        is_available = False
    
    return Response({
        "available": is_available,
        "caregiver_id": caregiver_id,
        "date": date_str,
        "time": time_str,
        "hourly_rate": float(caregiver.caregiver_profile.hourly_rate)
    })

class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """ViewSet for availability slots (caregivers only)"""
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AvailabilitySlot.objects.filter(caregiver=self.request.user)
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'caregiver':
            raise permissions.PermissionDenied("Only caregivers can set availability")
        serializer.save(caregiver=self.request.user)