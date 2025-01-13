# chat/urls.py
from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("chats/", views.ChatListingView.as_view(), name="home"),
    path("<str:room_name>/", views.room, name="room"),
]