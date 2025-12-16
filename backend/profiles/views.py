from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import CaregiverProfile, ClientProfile
from .serializers import CaregiverProfileSerializer, ClientProfileSerializer
from django.conf import settings

class CaregiverProfileView(generics.RetrieveUpdateAPIView):
    """Get or update caregiver profile"""
    serializer_class = CaregiverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get or create caregiver profile for current user
        profile, created = CaregiverProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'first_name': '',
                'last_name': '',
                'hourly_rate': 0,
                'city': ''
            }
        )
        return profile

class ClientProfileView(generics.RetrieveUpdateAPIView):
    """Get or update client profile"""
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get or create client profile for current user
        profile, created = ClientProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'first_name': '',
                'last_name': '',
                'phone_number': '',
                'address': '',
                'city': ''
            }
        )
        return profile

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_caregivers(request):
    """List all available caregivers (public endpoint)"""
    caregivers = CaregiverProfile.objects.filter(
        is_available=True
    ).order_by('-profile_score', '-created_at')
    
    # Basic filtering
    city = request.query_params.get('city', '')
    if city:
        caregivers = caregivers.filter(city__icontains=city)
    
    serializer = CaregiverProfileSerializer(caregivers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def caregiver_detail(request, pk):
    """Get specific caregiver details"""
    caregiver = get_object_or_404(CaregiverProfile, pk=pk, is_available=True)
    serializer = CaregiverProfileSerializer(caregiver)
    return Response(serializer.data)