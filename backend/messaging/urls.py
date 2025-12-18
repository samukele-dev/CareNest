from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'online-status', views.OnlineStatusViewSet, basename='online-status')

urlpatterns = [
    path('', include(router.urls)),
    path('start-conversation/', views.start_conversation, name='start-conversation'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('conversations/<int:conversation_id>/mark-read/', views.mark_conversation_read, name='mark-conversation-read'),
]