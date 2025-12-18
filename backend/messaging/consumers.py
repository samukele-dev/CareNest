import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, UserOnlineStatus
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join user's personal room for notifications
        self.user_room = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_room,
            self.channel_name
        )
        
        # Set user as online
        await self.set_online_status(True)
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and not self.user.is_anonymous:
            # Leave user room
            await self.channel_layer.group_discard(
                self.user_room,
                self.channel_name
            )
            
            # Set user as offline
            await self.set_online_status(False)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'send_message':
            await self.send_message(data)
        elif action == 'join_conversation':
            await self.join_conversation(data)
        elif action == 'typing':
            await self.handle_typing(data)
        elif action == 'mark_read':
            await self.mark_messages_read(data)
    
    async def send_message(self, data):
        """Handle sending a message"""
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        
        if not conversation_id or not content:
            return
        
        # Save message to database
        message = await self.save_message(conversation_id, content)
        
        if message:
            # Get conversation room
            conversation_room = f"conversation_{conversation_id}"
            
            # Send to conversation room
            await self.channel_layer.group_send(
                conversation_room,
                {
                    'type': 'chat_message',
                    'message': await self.message_to_dict(message)
                }
            )
            
            # Also send to recipient's personal room for notifications
            recipient = await self.get_other_participant(conversation_id, self.user.id)
            if recipient:
                recipient_room = f"user_{recipient.id}"
                await self.channel_layer.group_send(
                    recipient_room,
                    {
                        'type': 'new_message_notification',
                        'message': await self.message_to_dict(message),
                        'conversation_id': conversation_id
                    }
                )
    
    async def join_conversation(self, data):
        """Join a conversation room"""
        conversation_id = data.get('conversation_id')
        if conversation_id:
            conversation_room = f"conversation_{conversation_id}"
            await self.channel_layer.group_add(
                conversation_room,
                self.channel_name
            )
    
    async def handle_typing(self, data):
        """Handle typing indicators"""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        if conversation_id:
            conversation_room = f"conversation_{conversation_id}"
            await self.channel_layer.group_send(
                conversation_room,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'is_typing': is_typing
                }
            )
    
    async def mark_messages_read(self, data):
        """Mark messages as read"""
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await self.mark_conversation_read(conversation_id)
            
            # Notify other participant
            conversation_room = f"conversation_{conversation_id}"
            await self.channel_layer.group_send(
                conversation_room,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'conversation_id': conversation_id
                }
            )
    
    async def chat_message(self, event):
        """Receive chat message"""
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': event['message']
        }))
    
    async def new_message_notification(self, event):
        """Receive new message notification"""
        await self.send(text_data=json.dumps({
            'action': 'notification',
            'message': event['message'],
            'conversation_id': event['conversation_id']
        }))
    
    async def typing_indicator(self, event):
        """Receive typing indicator"""
        await self.send(text_data=json.dumps({
            'action': 'typing',
            'user_id': event['user_id'],
            'is_typing': event['is_typing']
        }))
    
    async def messages_read(self, event):
        """Receive messages read notification"""
        await self.send(text_data=json.dumps({
            'action': 'messages_read',
            'user_id': event['user_id'],
            'conversation_id': event['conversation_id']
        }))
    
    @database_sync_to_async
    def save_message(self, conversation_id, content):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )
            # Update conversation timestamp
            conversation.save()
            return message
        except Conversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def message_to_dict(self, message):
        return {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_email': message.sender.email,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        }
    
    @database_sync_to_async
    def get_other_participant(self, conversation_id, user_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.get_other_participant(self.user)
        except Conversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_conversation_read(self, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            updated = conversation.messages.filter(
                is_read=False
            ).exclude(
                sender=self.user
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            return updated
        except Conversation.DoesNotExist:
            return 0
    
    @database_sync_to_async
    def set_online_status(self, is_online):
        status_obj, created = UserOnlineStatus.objects.get_or_create(
            user=self.user,
            defaults={'is_online': is_online}
        )
        status_obj.is_online = is_online
        status_obj.save()