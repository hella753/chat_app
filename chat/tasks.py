import asyncio

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from user.models import User


@shared_task
def send_notification(user_id, message):
    user = User.objects.get(pk=user_id)
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications",
        {
            "type": "notify",
            "message": message,
            "recipient": user.username
        }
    )
    return None