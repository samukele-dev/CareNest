from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('check-email/', views.check_email_availability, name='check-email'),

]