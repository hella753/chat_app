import base64
import json
import uuid
from channels.db import database_sync_to_async, aclose_old_connections
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from chat.models import Chat, Message
from user.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    ChatConsumer handles WebSocket connections and messages.
    """
    async def connect(self):
        """
        Called when the websocket is handshaking as part of the connection process.
        """
        self.conversation = self.scope["url_route"]["kwargs"]["conversation"] # Get chat id from URL
        self.conv_group_name = f"chat_{self.conversation}" # Create a group
        self.user = self.scope['user'] # Get user object

        self.chat = await self.get_chat_instance()

        if not await self.is_user_online():
            # If the user is not online, add him to the list of online users
            await self.add_user_online()

        # Add user to the group
        await self.channel_layer.group_add(self.conv_group_name, self.channel_name)
        await self.accept()

        online_users = await self.get_online_users()
        event = {
            'type': 'online_users_handler',
            'online_users': online_users
        }
        # Send online users to the group
        await self.channel_layer.group_send(self.conv_group_name, event)

        # Get previous messages
        messages = await self.get_previous_messages(self.conversation)
        await self.send(text_data=json.dumps({
            'type': 'previous_messages',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        if await self.is_user_online():
            # If the user is online, remove him from the list of online users
            await self.remove_user_online()
            online_users = await self.get_online_users()
            event = {
                'type': 'online_users_handler',
                'online_users': online_users
            }
            # Send online users to the group
            await self.channel_layer.group_send(self.conv_group_name, event)

        # Remove user from the group
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

        # Save message to a database
        await self.save_message(user, conversation=self.conversation, file=file, message=message)

        if message.strip() != '':
            recipients = await self.get_chat_members(self.conversation)
            for recipient in recipients:
                if recipient != user:
                    # Send a message to a room group
                    await self.channel_layer.group_send(
                        self.conv_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'username': user.username,
                            'file': file,
                            'recipient': recipient.username
                        }
                    )
                    await self.channel_layer.group_send(
                        f"user_{recipient.id}_notifications",
                        {
                            'type': 'notify',
                            'message': f"New Message!",
                            'recipient': recipient.username,
                            'sender': self.user.username
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
        return [member for member in chat.members.all()]

    async def online_users_handler(self, event):
        """
        Called when the number of online users changes.
        """
        online_users = event.get('online_users', None)
        # Send a message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'online_users': online_users
        }))

    @database_sync_to_async
    def is_user_online(self):
        """
        Check if the user is online.
        :return: Boolean.
        """
        aclose_old_connections()
        return self.user in self.chat.users_online.all()

    @database_sync_to_async
    def add_user_online(self):
        """
        Add the user to chat's users_online field.
        """
        aclose_old_connections()
        self.chat.users_online.add(self.user)

    @database_sync_to_async
    def remove_user_online(self):
        """
        Remove the user from chat's users_online field.
        """
        aclose_old_connections()
        self.chat.users_online.remove(self.user)

    @database_sync_to_async
    def get_online_users(self):
        """
        Get a list of online users.
        :return: List of online users.
        """
        aclose_old_connections()
        return [user.username for user in self.chat.users_online.all()]

    @database_sync_to_async
    def get_chat_instance(self):
        """
        Get chat instance.
        :return: Chat instance.
        """
        aclose_old_connections()
        return Chat.objects.get(id=self.conversation)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    NotificationConsumer handles WebSocket connections and messages.
    """
    async def connect(self):
        """
        Called when the websocket is handshaking as part of the connection process.
        """
        self.user = self.scope['user']

        if self.user.is_anonymous:
            # If the user is not authenticated, close the connection
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}_notifications"

        # Add user to the group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def notify(self, event):
        """
        Called when a message is received from a room group.
        """
        message = event.get("message", "")
        recipient = event.get("recipient", "")
        sender = event.get("sender", "")

        if sender != "":
            # Send a message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'recipient': recipient,
                'sender': sender
            }))


class FriendRequestsConsumer(AsyncWebsocketConsumer):
    """
    FriendRequestsConsumer handles WebSocket connections and messages.
    """
    async def connect(self):
        self.user = self.scope['user']

        if self.user.is_anonymous:
            # If the user is not authenticated, close the connection
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}_request_notifications"

        # Add user to the group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        recipient = text_data_json.get("recipient", None)

        recipient = await self.get_user(recipient)

        await self.channel_layer.group_send(
            f"user_{recipient.id}_notifications",
            {
                'type': 'notify',
                'message': f"New Friend Request",
                'recipient': recipient.username,
                'sender': self.user.username
            }
        )

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)