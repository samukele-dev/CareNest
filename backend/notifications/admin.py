# notifications/admin.py
from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'notification_type', 'title_short', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    list_per_page = 20
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'email_notifications', 'push_notifications', 'updated_at')
    list_filter = ('email_notifications', 'push_notifications')
    search_fields = ('user__email',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'