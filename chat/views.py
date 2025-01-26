from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DeleteView
from chat.forms import ChatCreationForm, ChatDeletionForm
from chat.models import Chat
from user.models import User


@method_decorator(login_required, name="dispatch")
class ChatListingView(ListView):
    """
    List all chats that the user is a member of.
    """
    template_name = "chat/home.html"
    model = Chat
    context_object_name = "chats"

    def get_queryset(self):
        return Chat.objects.filter(
            members=self.request.user
        ).prefetch_related("members").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.is_anonymous and isinstance(user, User):
            context["friends"] = user.friends.all()
        return context


@method_decorator(login_required, name="dispatch")
class ChatDetailView(ListView):
    """
    List all messages in a chat.
    """
    template_name = "chat/conversation.html"
    model = Chat
    context_object_name = "messages"

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs.get("conversation"))
        return chat.messages.select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_formats"] = ["png", "jpg", "jpeg", "gif", "svg", "webp"]
        context["chats"] = Chat.objects.filter(members=self.request.user).prefetch_related("members")
        context["conversation"] = self.kwargs.get("conversation")
        context["chat"] = get_object_or_404(Chat, id=context["conversation"])
        return context


@method_decorator(login_required, name="dispatch")
class ChatCreationView(CreateView):
    """
    Create a new chat.
    """
    form_class = ChatCreationForm
    template_name = "chat/home.html"
    success_url = reverse_lazy("chat:home")
    context_object_name = "chats"

    def form_invalid(self, form):
        print(form.errors)
        return redirect("chat:home")

    def form_valid(self, form):
        friends = form.cleaned_data.get("friends_checkboxes")
        chat_instance = form.save(commit=False)
        if len(friends) == 1:
            chat_instance.is_group = False
        else:
            chat_instance.is_group = True
        chat_instance.save()

        all_members = list(friends) + [self.request.user]
        existing_chat = Chat.objects.filter(members__in=all_members)
        for chat in existing_chat:
            if set(chat.members.all()) == set(all_members):
                return self.form_invalid(form)
        chat_instance.members.add(*friends, self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class ChatDeletionView(DeleteView):
    """
    Delete a chat
    """
    form_class = ChatDeletionForm
    success_url = reverse_lazy("chat:home")
    template_name = "chat/home.html"

    def get_object(self, queryset=None):
        conversation = self.kwargs.get('conversation')
        return get_object_or_404(Chat, id=conversation)