from django.db import models


class Chat(models.Model):
    """
    Chat model
    """
    name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField('user.User', related_name='chats')
    users_online = models.ManyToManyField('user.User', related_name='online_in_chat', blank=True)
    is_group = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    """
    Message model for chat
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    author = models.ForeignKey('user.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text


