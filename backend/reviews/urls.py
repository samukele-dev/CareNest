from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('caregiver/<int:caregiver_id>/', views.caregiver_reviews, name='caregiver-reviews'),
    path('caregiver/<int:caregiver_id>/stats/', views.ReviewStatsView.as_view(), name='review-stats'),
    path('available/', views.available_to_review, name='available-to-review'),
]