from django.shortcuts import render
from django.views.generic import ListView
from chat.models import Chat


class ChatListingView(ListView):
    template_name = "chat/home.html"
    model = Chat
    context_object_name = "chats"

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user)


def room(request, room_name):
    queryset = Chat.objects.filter(members=request.user)

    chat = Chat.objects.get(id=room_name)
    messages = chat.messages.select_related('author').all()

    context = {"room_name": room_name, "chats": queryset, "chat": chat, "messages": messages}
    return render(request, "chat/room.html", context=context)
