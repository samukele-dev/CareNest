"""
CareNest Pro - Admin Configuration
Version: 4.3.0 - Fixed duplicate fields
Description: Advanced administrative interface for managing Caregivers, Clients, 
and Financial Transactions.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CaregiverProfile, ClientProfile, Appointment, 
    Availability, Review, ProfileNotification, 
    CareLog, Payment, ProfileAttachment
)

# =============================================================================
# 1. CAREGIVER ADMIN
# =============================================================================

@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name_display', 'user_email', 'hourly_rate', 'experience_years', 
        'average_rating', 'id_verified', 'background_check_verified', 'is_active'
    )
    list_filter = (
        'is_active', 'id_verified', 'background_check_verified', 
        'is_featured', 'city'
    )
    search_fields = ('first_name', 'last_name', 'user__email', 'city', 'bio')
    readonly_fields = ('id', 'average_rating', 'total_reviews', 'profile_completion_percentage', 'created_at', 'updated_at')
    fieldsets = (
        ('Account Info', {
            'fields': ('user', 'id', 'is_active', 'is_featured')
        }),
        ('Personal Identity', {
            'fields': ('first_name', 'last_name', 'profile_image', 'bio')
        }),
        ('Professional Details', {
            'fields': ('hourly_rate', 'experience_years', 'specialties', 'profile_completion_percentage')
        }),
        ('Verification Status', {
            'fields': ('id_verified', 'background_check_verified', 'id_document', 'insurance_policy_number')
        }),
        ('Location', {
            'fields': ('location', 'city', 'postal_code', 'latitude', 'longitude')
        }),
        ('Marketplace Metrics', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login_as_caregiver'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Caregiver')
    def full_name_display(self, obj):
        return obj.full_name
    
    @admin.display(description='Email')
    def user_email(self, obj):
        return obj.user.email if obj.user else 'No user'

# =============================================================================
# 2. CLIENT ADMIN
# =============================================================================

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'user_email', 'city', 'preferred_care_type', 'is_premium_member')
    list_filter = ('is_premium_member', 'city')
    search_fields = ('user__email', 'first_name', 'last_name', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    @admin.display(description='Client')
    def full_name_display(self, obj):
        return obj.full_name
    
    @admin.display(description='Email')
    def user_email(self, obj):
        return obj.user.email if obj.user else 'No user'

# =============================================================================
# 3. APPOINTMENT ADMIN
# =============================================================================

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'caregiver_display', 'client_display', 'date', 'start_time', 'status', 'total_amount', 'is_paid')
    list_filter = ('status', 'is_paid', 'date')
    search_fields = ('caregiver__first_name', 'caregiver__last_name', 'client__first_name', 'client__last_name', 'service_type')
    date_hierarchy = 'date'
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_amount')
    actions = ['mark_as_paid', 'cancel_appointments']
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name
    
    @admin.display(description='Client')
    def client_display(self, obj):
        return obj.client.full_name

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    mark_as_paid.short_description = "Mark selected appointments as Paid"

# =============================================================================
# 4. FINANCIALS & LOGS
# =============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_display', 'caregiver_display', 'amount', 'status', 'paid_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'caregiver__first_name', 'caregiver__last_name', 'stripe_charge_id')
    readonly_fields = ('id', 'created_at', 'net_to_caregiver')
    
    @admin.display(description='Client')
    def client_display(self, obj):
        return obj.client.full_name
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name

@admin.register(CareLog)
class CareLogAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'caregiver_display', 'client_display', 'clock_in', 'clock_out')
    search_fields = ('caregiver__first_name', 'caregiver__last_name', 'client__first_name', 'client__last_name')
    readonly_fields = ('created_at',)
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name
    
    @admin.display(description='Client')
    def client_display(self, obj):
        return obj.client.full_name
    
    @admin.display(description='Appointment')
    def appointment_id(self, obj):
        return obj.appointment.id

# =============================================================================
# 5. SUPPORTING MODELS
# =============================================================================

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('caregiver_display', 'day_of_week', 'specific_date', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('caregiver__first_name', 'caregiver__last_name')
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('caregiver_display', 'client_display', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible')
    search_fields = ('caregiver__first_name', 'caregiver__last_name', 'client__first_name', 'client__last_name')
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name
    
    @admin.display(description='Client')
    def client_display(self, obj):
        return obj.client.full_name

@admin.register(ProfileNotification)
class ProfileNotificationAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    
    @admin.display(description='User')
    def user_display(self, obj):
        return obj.user.email

@admin.register(ProfileAttachment)
class ProfileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('caregiver_display', 'title', 'is_verified', 'expiry_date')
    list_filter = ('is_verified',)
    search_fields = ('caregiver__first_name', 'caregiver__last_name', 'title')
    
    @admin.display(description='Caregiver')
    def caregiver_display(self, obj):
        return obj.caregiver.full_name