from django.urls import re_path, path
from . import consumers
from .consumers import NotificationConsumer, FriendRequestsConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<conversation>\w+)/$", consumers.ChatConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/friend_requests/', FriendRequestsConsumer.as_asgi()),
]
