"""
CareNest Pro - Complete Profiles Views
Aligned with Enterprise Database Schema v4.0.0
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
import logging

# Import the models exactly as defined in your Enterprise Schema
from .models import (
    CaregiverProfile, ClientProfile, Appointment, 
    Availability, Review, ProfileNotification,
    AppointmentStatus, NotificationType, PaymentStatus
)
from .serializers import (
    CaregiverProfileSerializer, ClientProfileSerializer,
    AppointmentSerializer, AvailabilitySerializer,
    ReviewSerializer, NotificationSerializer
)

logger = logging.getLogger(__name__)

# =============================================================================
# 1. CAREGIVER SIMPLE VIEWS
# =============================================================================

class CaregiverMeView(APIView):
    """
    GET /api/profiles/caregiver/me/ - Get profile
    POST /api/profiles/caregiver/me/ - Create profile
    PATCH /api/profiles/caregiver/me/ - Update profile
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = CaregiverProfile.objects.get(user=request.user)
            serializer = CaregiverProfileSerializer(profile)
            data = serializer.data
            data['exists'] = True
            return Response(data)
        except CaregiverProfile.DoesNotExist:
            user_data = {
                "email": request.user.email,
                "username": request.user.username,
            }
            if hasattr(request.user, 'first_name'):
                user_data["first_name"] = request.user.first_name or ""
            else:
                user_data["first_name"] = ""
            
            if hasattr(request.user, 'last_name'):
                user_data["last_name"] = request.user.last_name or ""
            else:
                user_data["last_name"] = ""
            
            return Response({
                "exists": False,
                "message": "Profile not found",
                "user": user_data
            }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        if CaregiverProfile.objects.filter(user=request.user).exists():
            return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        serializer = CaregiverProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        try:
            profile = CaregiverProfile.objects.get(user=request.user)
        except CaregiverProfile.DoesNotExist:
            first_name = getattr(request.user, 'first_name', "")
            last_name = getattr(request.user, 'last_name', "")
            profile = CaregiverProfile.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name
            )
        
        serializer = CaregiverProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CaregiverDashboardStatsView(APIView):
    """Business Intelligence following the schema metrics."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = CaregiverProfile.objects.get(user=request.user)
        except CaregiverProfile.DoesNotExist:
            return Response({"exists": False, "stats": {"total_earnings": 0, "hours_worked": 0}})
        
        appointments = Appointment.objects.filter(caregiver=profile)
        total_earnings = appointments.filter(status=AppointmentStatus.COMPLETED, is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_hours = appointments.filter(status=AppointmentStatus.COMPLETED).aggregate(Sum('duration_hours'))['duration_hours__sum'] or 0
        
        return Response({
            "exists": True,
            "total_earnings": float(total_earnings),
            "hours_worked": float(total_hours),
            "rating": float(profile.average_rating),
            "total_reviews": profile.total_reviews,
            "upcoming_appointments": appointments.filter(status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED], date__gte=timezone.now().date()).count()
        })

class CaregiverUpdateAvailabilityView(APIView):
    """Maps frontend day strings to DayOfWeek integer choices in the schema."""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        profile = get_object_or_404(CaregiverProfile, user=request.user)
        schedule_data = request.data.get('schedule', [])
        
        Availability.objects.filter(caregiver=profile).delete()
        
        day_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        for slot in schedule_data:
            if slot.get('active'):
                Availability.objects.create(
                    caregiver=profile,
                    day_of_week=day_map.get(slot.get('day'), 0),
                    start_time=slot.get('start'),
                    end_time=slot.get('end'),
                    is_active=True
                )
        return Response({'status': 'Availability updated'})

class CompleteCaregiverProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        profile, _ = CaregiverProfile.objects.get_or_create(user=request.user)
        data = request.data
        for field in ['bio', 'hourly_rate', 'experience_years', 'location']:
            if field in data: setattr(profile, field, data[field])
        if 'specialties' in data:
            profile.specialties = data['specialties'] if isinstance(data['specialties'], list) else [data['specialties']]
        profile.save()
        return Response(CaregiverProfileSerializer(profile).data)

# =============================================================================
# 2. CLIENT VIEWS
# =============================================================================

class ClientMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            profile = ClientProfile.objects.get(user=request.user)
            data = ClientProfileSerializer(profile).data
            data['exists'] = True
            return Response(data)
        except ClientProfile.DoesNotExist:
            return Response({"exists": False}, status=404)

    def post(self, request):
        if ClientProfile.objects.filter(user=request.user).exists():
            return Response({"error": "Exists"}, status=400)
        serializer = ClientProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# =============================================================================
# 3. VIEWSETS - Mapped to Enterprise Schema v4.0.0
# =============================================================================

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    CRITICAL FIX: Maps incoming request data to match the 
    Appointment model's strict field requirements.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'caregiver_profile'):
            return Appointment.objects.filter(caregiver=user.caregiver_profile)
        if hasattr(user, 'client_profile'):
            return Appointment.objects.filter(client=user.client_profile)
        return Appointment.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Interprets frontend keys and reformats them to satisfy model constraints:
        - 'client' auto-assigned from user
        - 'service' -> 'service_type'
        - 'hourly_rate' -> 'hourly_rate_at_booking'
        - Time string cleaning for 'start_time' and 'end_time'
        """
        data = request.data.copy()
        
        # 1. Map Schema-Required Fields
        if 'service' in data and 'service_type' not in data:
            data['service_type'] = data['service']
        
        if 'hourly_rate' in data and 'hourly_rate_at_booking' not in data:
            data['hourly_rate_at_booking'] = data['hourly_rate']

        # 2. Time Cleaning (Fixes 'Time has wrong format' error)
        # Strips milliseconds/seconds: '14:30:00.000' -> '14:30'
        for time_field in ['start_time', 'end_time']:
            if time_field in data and data[time_field]:
                data[time_field] = data[time_field].split('.')[0][:5]

        # 3. Auto-assignment of Client (Fixes 'client is required' error)
        try:
            client_profile = ClientProfile.objects.get(user=request.user)
            data['client'] = client_profile.id
        except ClientProfile.DoesNotExist:
            pass

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Detailed error logging for terminal debugging
        print(f"DEBUG: Appointment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        qs = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).order_by('date', 'start_time')
        return Response(self.get_serializer(qs, many=True).data)

class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Availability.objects.filter(caregiver__user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    """Strictly matches the post-appointment Review schema."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return ProfileNotification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success'})

# =============================================================================
# 4. DISCOVERY & UTILITIES
# =============================================================================

class CaregiverDiscoveryView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # Parse query parameters
            min_rate = request.GET.get('min_rate')
            max_rate = request.GET.get('max_rate')
            sort = request.GET.get('sort', 'recommended')
            
            # Start with base queryset
            qs = CaregiverProfile.objects.filter(is_active=True)
            
            # Apply rate filtering if provided
            if min_rate:
                try:
                    qs = qs.filter(hourly_rate__gte=float(min_rate))
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Invalid min_rate parameter"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if max_rate:
                try:
                    qs = qs.filter(hourly_rate__lte=float(max_rate))
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Invalid max_rate parameter"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Apply sorting
            if sort == 'recommended':
                qs = qs.order_by('-average_rating', '-total_reviews')
            elif sort == 'rate_low':
                qs = qs.order_by('hourly_rate')
            elif sort == 'rate_high':
                qs = qs.order_by('-hourly_rate')
            elif sort == 'experience':
                qs = qs.order_by('-experience_years')
            
            # Limit results
            qs = qs[:20]
            
            # Serialize with error handling
            serializer = CaregiverProfileSerializer(qs, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Caregiver discovery error: {str(e)}")
            return Response(
                {"error": "Internal server error in discovery endpoint"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({"status": "healthy", "timestamp": timezone.now().isoformat()})

class DebugUrlsView(APIView):
    """Utility to verify routing against the enterprise model views."""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        from django.urls import get_resolver
        from django.urls.resolvers import URLPattern, URLResolver
        def extract_urls(urlpatterns, base=''):
            urls = []
            for pattern in urlpatterns:
                if isinstance(pattern, URLPattern):
                    urls.append({'pattern': base + str(pattern.pattern), 'name': pattern.name})
                elif isinstance(pattern, URLResolver):
                    urls.extend(extract_urls(pattern.url_patterns, base + str(pattern.pattern)))
            return urls
        return Response({'routes': [u for u in extract_urls(get_resolver().url_patterns) if 'profiles' in u['pattern']]})


class DebugUUIDErrorView(APIView):
    """Simple debug view that doesn't require auth"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        import traceback
        import json
        
        try:
            print("\n=== DEBUG UUID ERROR ===")
            print(f"Request path: {request.path}")
            print(f"Query params: {dict(request.GET)}")
            
            # 1. First, check if we can even query the database
            print("\n1. Testing database connection...")
            count = CaregiverProfile.objects.count()
            print(f"   Total caregivers in DB: {count}")
            
            # 2. Try to get one caregiver
            print("\n2. Testing single caregiver query...")
            if count > 0:
                caregiver = CaregiverProfile.objects.first()
                print(f"   First caregiver ID: {caregiver.id}")
                print(f"   ID type: {type(caregiver.id)}")
                print(f"   First name: {caregiver.first_name}")
                print(f"   Last name: {caregiver.last_name}")
                
                # Try to convert to string
                try:
                    id_str = str(caregiver.id)
                    print(f"   ID as string: {id_str}")
                    print(f"   Is valid UUID: ✓")
                except Exception as e:
                    print(f"   ERROR converting ID to string: {e}")
            
            # 3. Try the actual query from discovery
            print("\n3. Testing discovery query logic...")
            qs = CaregiverProfile.objects.filter(is_active=True)[:3]
            print(f"   Found {qs.count()} active caregivers")
            
            for i, caregiver in enumerate(qs):
                print(f"\n   Caregiver {i+1}:")
                print(f"     ID: {caregiver.id}")
                
                # Try to access all model fields
                model_fields = [
                    'first_name', 'last_name', 'bio', 'hourly_rate',
                    'experience_years', 'specialties', 'location', 'city',
                    'average_rating', 'total_reviews'
                ]
                
                for field in model_fields:
                    try:
                        value = getattr(caregiver, field)
                        print(f"     {field}: {value}")
                    except Exception as e:
                        print(f"     ERROR getting {field}: {e}")
            
            # 4. Try serialization
            print("\n4. Testing serialization...")
            if qs.exists():
                from .serializers import CaregiverProfileSerializer
                
                try:
                    serializer = CaregiverProfileSerializer(qs.first())
                    data = serializer.data
                    print(f"   Serialization successful!")
                    print(f"   Serialized fields: {list(data.keys())[:5]}...")
                    
                    # Check ID in serialized data
                    if 'id' in data:
                        print(f"   Serialized ID: {data['id']} (type: {type(data['id']).__name__})")
                        
                except Exception as e:
                    print(f"   Serialization ERROR: {e}")
                    print(f"   Traceback:\n{traceback.format_exc()}")
            
            print("\n=== END DEBUG ===")
            
            return Response({
                "status": "debug_complete",
                "caregiver_count": count,
                "message": "Check Django console for detailed output"
            })
            
        except Exception as e:
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "request_info": {
                    "path": request.path,
                    "method": request.method,
                    "params": dict(request.GET)
                }
            }
            print(f"\n=== FATAL ERROR ===")
            print(json.dumps(error_details, indent=2))
            
            return Response(error_details, status=500)