from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from notifications.utils import NotificationService

from .models import Conversation, Message, UserOnlineStatus
from .serializers import (
    ConversationSerializer, MessageSerializer,
    CreateMessageSerializer, OnlineStatusSerializer
)

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user, is_active=True)
    
    def list(self, request, *args, **kwargs):
        """Override list to properly handle pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('created_at')
        
        # Mark messages as read
        if request.user != conversation.messages.last().sender:
            conversation.messages.filter(is_read=False).exclude(sender=request.user).update(
                is_read=True, read_at=timezone.now()
            )
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation"""
        conversation = self.get_object()
        conversation.is_active = False
        conversation.save()
        return Response({"status": "archived"})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search messages by content"""
        query = request.GET.get('q', '')
        messages = Message.objects.filter(
            conversation__participants=request.user,
            content__icontains=query
        )
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)
    
    def create(self, request, *args, **kwargs):
        serializer = CreateMessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Get conversation and recipient from validated data
            # These are already User/Conversation objects from serializer validation
            conversation = data.get('conversation')
            recipient = data.get('recipient')  # This is the User object
            
            # If we have a conversation, use it
            if conversation:
                # Make sure current user is in conversation
                if request.user not in conversation.participants.all():
                    return Response(
                        {"error": "You are not a participant in this conversation"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get recipient from conversation (other participant)
                # First, check if conversation model has get_other_participant method
                if hasattr(conversation, 'get_other_participant'):
                    recipient = conversation.get_other_participant(request.user)
                else:
                    # Fallback: get other participant manually
                    recipient = conversation.participants.exclude(id=request.user.id).first()
                
                if not recipient:
                    return Response(
                        {"error": "Could not determine recipient from conversation"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            else:
                # Create new conversation with recipient
                recipient = data['recipient']  # From serializer validation
                
                # Check if conversation already exists between these users
                existing_conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(
                    participants=recipient
                ).filter(
                    is_active=True
                ).first()
                
                if existing_conversation:
                    conversation = existing_conversation
                else:
                    # Create new conversation
                    conversation = Conversation.objects.create(is_active=True)
                    conversation.participants.add(request.user, recipient)
                    conversation.save()
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=data['content'],
                booking_id=data.get('booking_id')
            )
            
            # Update conversation timestamp
            conversation.save()
            
            # Send notification to recipient
            notification_service = NotificationService()
            
            # Get sender name - FIXED: Use get_username() or email
            sender_name = request.user.get_username() or request.user.email
            
            notification_service.send_new_message_notification(
                user=recipient,  # The message recipient (User object)
                context={
                    'sender_name': sender_name,  # FIXED: Use get_username() not get_full_name()
                    'message_preview': data['content'][:50],  # First 50 chars
                    'conversation_id': conversation.id
                }
            )
            
            return Response(
                MessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_conversation(request):
    """Start a new conversation with another user"""
    recipient_id = request.data.get('recipient_id')
    
    if not recipient_id:
        return Response(
            {"error": "recipient_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Recipient not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=recipient
    ).filter(
        is_active=True
    ).first()
    
    if existing_conversation:
        serializer = ConversationSerializer(existing_conversation, context={'request': request})
        return Response(serializer.data)
    
    # Create new conversation
    conversation = Conversation.objects.create(is_active=True)
    conversation.participants.add(request.user, recipient)
    conversation.save()
    
    serializer = ConversationSerializer(conversation, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Get total unread messages count for current user"""
    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(
        sender=request.user
    ).count()
    
    return Response({"unread_count": count})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_conversation_read(request, conversation_id):
    """Mark all messages in a conversation as read"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    updated = conversation.messages.filter(
        is_read=False
    ).exclude(
        sender=request.user
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({"marked_read": updated})

class OnlineStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for online status"""
    serializer_class = OnlineStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserOnlineStatus.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def set_online(self, request):
        """Set user as online"""
        status_obj, created = UserOnlineStatus.objects.get_or_create(
            user=request.user,
            defaults={'is_online': True}
        )
        status_obj.is_online = True
        status_obj.save()
        
        return Response({"status": "online"})
    
    @action(detail=False, methods=['post'])
    def set_offline(self, request):
        """Set user as offline"""
        status_obj, created = UserOnlineStatus.objects.get_or_create(
            user=request.user,
            defaults={'is_online': False}
        )
        status_obj.is_online = False
        status_obj.save()
        
        return Response({"status": "offline"})