"""
CareNest Pro - PROFILES APP URL CONFIGURATION
All URLs here are prefixed with: /api/profiles/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register viewsets that work 

router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'availability', views.AvailabilityViewSet, basename='availability')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

# List of all URL patterns for the profiles app
urlpatterns = [
    path('', include(router.urls)),

    path('debug/urls/', views.DebugUrlsView.as_view(), name='debug-urls'),

    path('debug/uuid-error/', views.DebugUUIDErrorView.as_view(), name='debug-uuid-error'),

    
    # ====== CAREGIVER ENDPOINTS ======
    # /api/profiles/caregiver/me/
    path('caregiver/me/', views.CaregiverMeView.as_view(), name='caregiver-me'),
    
    # /api/profiles/caregiver/dashboard_stats/
    path('caregiver/dashboard_stats/', views.CaregiverDashboardStatsView.as_view(), name='caregiver-dashboard-stats'),
    
    # /api/profiles/caregiver/update_availability/
    path('caregiver/update_availability/', views.CaregiverUpdateAvailabilityView.as_view(), name='caregiver-update-availability'),
    
    # /api/profiles/caregiver/complete_profile/
    path('caregiver/complete_profile/', views.CompleteCaregiverProfileView.as_view(), name='complete-caregiver-profile'),
    
    # ====== CLIENT ENDPOINTS ======
    # /api/profiles/client/me/
    path('client/me/', views.ClientMeView.as_view(), name='client-me'),
    
    # ====== DISCOVERY & SEARCH ======
    # /api/profiles/caregiver/discovery/
    path('caregiver/discovery/', views.CaregiverDiscoveryView.as_view(), name='caregiver-discovery'),
    
    # ====== HEALTH CHECK ======
    # /api/profiles/health/
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]