import base64
import json
import uuid
from channels.db import database_sync_to_async, aclose_old_connections
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from chat.models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    ChatConsumer class is a subclass of AsyncWebsocketConsumer.
    It handles WebSocket connections and messages.
    """
    async def connect(self):
        """
        Called when the websocket is handshaking as part of the connection process.
        """
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
        """
        Called when the WebSocket closes for any reason.
        """
        await self.channel_layer.group_discard(self.conv_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Called when the consumer receives data.
        :param text_data: Received data
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope['user']
        file = text_data_json.get("file", None)

        await self.save_message(user, conversation=self.conversation, file=file, message=message)

        if message.strip() != '':
            recipients = await self.get_chat_members(self.conversation)
            for recipient in recipients:
                if recipient != user.username:
                    # Send a message to a room group
                    await self.channel_layer.group_send(
                        self.conv_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'username': user.username,
                            'file': file,
                            'recipient': recipient
                        }
                    )

    async def chat_message(self, event):
        """
        Called when a message is received from a room group.
        :param event: Received event
        """
        message = event["message"]
        username = event['username']
        file = event["file"]

        # Send a message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'file': file,
        }))

    @database_sync_to_async
    def save_message(self, user, conversation, message, file):
        """
        Save message to a database
        :param user: User object
        :param conversation: chat id
        :param message: message text
        :param file: file
        :return: None
        """
        aclose_old_connections()

        mime_type_map = {
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/plain': 'txt',
            'application/zip': 'zip',
        }

        if file:
            frmt, file_str = file.split(';base64,')
            ext = frmt.split('/')[-1]

            mime_tp = frmt.split(':')[1]

            if ext not in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']:
                ext = mime_type_map.get(mime_tp, 'txt')

            file_name = f"{uuid.uuid4()}.{ext}"
            file_content = ContentFile(base64.b64decode(file_str), name=file_name)
        else:
            file_content = None
        if message.strip() != '':
            chat, created = Chat.objects.get_or_create(id=conversation)
            Message.objects.create(chat=chat, author=user, file=file_content, text=message, read=False)

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
                     'file': message.file.url if message.file else None,
                     'created_at': message.created_at.strftime("%Y-%m-%d %H:%M:%S")}
                    for message in chat.messages.all()]
        except Chat.DoesNotExist:
            return []

    @database_sync_to_async
    def get_chat_members(self, conversation):
        """
        Retrieve members of the chat.
        """
        aclose_old_connections()
        chat = Chat.objects.get(id=conversation)
        return [member.username for member in chat.members.all()]