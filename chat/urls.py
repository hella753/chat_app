from django.conf import settings
from django.urls import path, include

from . import views

app_name = "chat"

urlpatterns = [
    path("chats/", views.ChatListingView.as_view(), name="home"),
    path("create/", views.ChatCreationView.as_view(), name="create"),
    path("<str:conversation>/", views.ChatDetailView.as_view(), name="conversation"),
]