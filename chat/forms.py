from django import forms
from chat.models import Chat


class ChatCreationForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = []


class ChatDeletionForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = []