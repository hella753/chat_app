from django import forms
from chat.models import Chat
from user.models import User


class ChatCreationForm(forms.ModelForm):
    friends_checkboxes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Chat
        fields = ["name", "friends_checkboxes"]


class ChatDeletionForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = []