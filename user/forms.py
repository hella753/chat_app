from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from user.models import User


class RegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    class Meta:
        model = User
        fields = ['first_name',
                  'last_name',
                  'username',
                  'email',
                  'password1',
                  'password2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")
        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e)
        return cleaned_data


class ProfileUpdateForm(ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'image', 'username']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }


class UpdatePasswordForm(ModelForm):
    """
    Form for updating user password.
    """
    current_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['current_password', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        current_password = cleaned_data.get("current_password")
        if not self.instance.check_password(current_password):
            raise ValidationError("Invalid password")
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        user.set_password(password)
        if commit:
            user.save()
        return user