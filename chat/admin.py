from django.contrib import admin

from chat.models import Chat, Message

# Register your models here.

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_group', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_group',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'author', 'created_at')
    list_filter = ('chat', 'author')
