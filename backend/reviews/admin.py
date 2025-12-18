from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'caregiver_name', 'reviewer_name', 'rating', 'created_at', 'has_response')
    list_filter = ('rating', 'would_recommend', 'created_at')
    search_fields = ('caregiver__email', 'reviewer__email', 'comment')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')
    
    def caregiver_name(self, obj):
        return obj.caregiver.caregiver_profile.first_name if hasattr(obj.caregiver, 'caregiver_profile') else obj.caregiver.email
    
    def reviewer_name(self, obj):
        return obj.reviewer.client_profile.first_name if hasattr(obj.reviewer, 'client_profile') else obj.reviewer.email
    
    def has_response(self, obj):
        return bool(obj.caregiver_response)
    has_response.boolean = True