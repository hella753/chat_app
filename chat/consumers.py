import json
from channels.db import database_sync_to_async, aclose_old_connections
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Called on connection.
        self.conversation = self.scope["url_route"]["kwargs"]["conversation"]
        self.conv_group_name = f"chat_{self.conversation}"

        await self.channel_layer.group_add(self.conv_group_name, self.channel_name)

        await self.accept()

        messages = await self.get_previous_messages(self.conversation)

        await self.send(text_data=json.dumps({
            'type': 'previous_messages',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # Leave a room group
        await self.channel_layer.group_discard(self.conv_group_name, self.channel_name)

    # Receive a message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope['user']

        await self.save_message(user, conversation=self.conversation, message=message)

        # Send a message to a room group
        await self.channel_layer.group_send(
            self.conv_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    # Receive a message from conversation group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']

        # Send a message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, user, conversation, message):
        """
        Save message to a database
        :param user: User object
        :param conversation: chat id
        :param message: message text
        :return: None
        """
        aclose_old_connections()
        chat, created = Chat.objects.get_or_create(id=conversation)
        Message.objects.create(chat=chat, author=user, text=message)

    @database_sync_to_async
    def get_previous_messages(self, conversation):
        """
        Get previous messages from a database
        :param conversation: chat id
        :return: list of messages
        """
        aclose_old_connections()
        try:
            chat = Chat.objects.get(id=conversation)
            return [{'username': message.author.username,
                     'text': message.text,
                     'created_at': message.created_at.strftime("%Y-%m-%d %H:%M:%S")}
                    for message in chat.messages.all()]
        except Chat.DoesNotExist:
            return []