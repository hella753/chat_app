from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message


@receiver(post_save, sender=Message)
def send_notification_signal(sender, instance, created, **kwargs):
    """
    Send a notification to the recipient of the message.
    """
    from chat.tasks import send_notification
    if created:
        user_id = instance.chat.members.exclude(id=instance.author.id).first().id
        send_notification(user_id, "You have a new message!")
