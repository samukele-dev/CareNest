# project_root/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # ====== APP URLs (use app-specific urls.py files) ======
    path('api/users/', include('users.urls')),
    path('api/profiles/', include('profiles.urls')),  # All profiles endpoints are handled here
    path('api/bookings/', include('bookings.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/payroll/', include('payroll.urls')),
    path('api/contracts/', include('contracts.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # ====== HEALTH & API ROOT ======
    path('health/', lambda request: JsonResponse({'status': 'healthy'}), name='health-check'),
    
    path('api/', lambda request: JsonResponse({
        'message': 'CareNest API',
        'endpoints': {
            'auth': '/api/auth/',
            'profiles': '/api/profiles/',
            'users': '/api/users/',
            'bookings': '/api/bookings/',
        }
    }), name='api-root'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)