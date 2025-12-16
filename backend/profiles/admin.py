from django.contrib import admin
from .models import CaregiverProfile, ClientProfile

@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'hourly_rate', 'is_available', 'profile_score')
    list_filter = ('is_available', 'city', 'is_featured')
    search_fields = ('first_name', 'last_name', 'city', 'user__email')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'care_type')
    list_filter = ('care_type', 'city')
    search_fields = ('first_name', 'last_name', 'city', 'user__email')