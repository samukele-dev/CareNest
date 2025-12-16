from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'booking-requests', views.BookingRequestViewSet, basename='booking-request')
router.register(r'availability', views.AvailabilitySlotViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
    path('create-request/', views.create_booking_request, name='create-booking-request'),
    path('caregiver/<int:caregiver_id>/check-availability/', views.check_caregiver_availability, name='check-availability'),
]