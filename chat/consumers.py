import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join a room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        messages = await self.get_previous_messages(self.room_name)
        await self.send(text_data=json.dumps({
            'type': 'previous_messages',
            'messages': messages
        }))


    async def disconnect(self, close_code):
        # Leave a room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive a message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope['user']

        await self.save_message(user, room_name=self.room_name, message=message)

        # Send a message to a room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    # Receive a message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']

        # Send a message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, user, room_name, message):
        chat, created = Chat.objects.get_or_create(id=room_name)
        Message.objects.create(chat=chat, author=user, text=message)

    @sync_to_async
    def get_previous_messages(self, room_name):
        chat = Chat.objects.get(id=room_name)
        return [{'username': message.author.username,
                 'text': message.text,
                 'created_at': message.created_at.strftime("%Y-%m-%d %H:%M:%S")} for message in chat.messages.all()]