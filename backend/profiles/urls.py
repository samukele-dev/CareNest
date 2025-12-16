from django.urls import path
from . import views

urlpatterns = [
    # User's own profiles
    path('caregiver/', views.CaregiverProfileView.as_view(), name='caregiver-profile'),
    path('client/', views.ClientProfileView.as_view(), name='client-profile'),
    
    # Public endpoints
    path('caregivers/', views.list_caregivers, name='list-caregivers'),
    path('caregivers/<int:pk>/', views.caregiver_detail, name='caregiver-detail'),
]